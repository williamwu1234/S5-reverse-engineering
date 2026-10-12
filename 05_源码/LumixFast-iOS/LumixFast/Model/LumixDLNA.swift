 // LumixDLNA.swift
 //
 // DLNA ContentDirectory client for the Lumix camera's file browser/transfer.
 // Reverse-engineered from LUMIX Sync (see PROTOCOL_AUDIT §4):
 //   - Control: POST http://<ip>:60606/Server0/CDS_control  (SOAP Browse)
 //   - Data:    http://<ip>:60606/Lumix/Server0/ddd
 //   - User-Agent: "Panasonic MIL DLNA CP UPnP/1.0"
 //   - Thumbnails: request header "X-CONVERT: MediumSize|SmallSize"
 //   - Size: response header "X-FILE_SIZE"
 //
 import Foundation

 struct LumixFileItem: Identifiable, Equatable {
     let id: String
     let parentID: String
     let title: String
     let upnpClass: String
     let res: String?          // download URL
     let size: Int64?
     var identifier: String { id }

     var isContainer: Bool { upnpClass.contains("container") }
     var isMedia: Bool { upnpClass.contains("item") && !upnpClass.contains("container") }
 }

 final class LumixDLNA {

    private let base: String       // "ip:60606"
    private let session: URLSession

    init(ip: String) {
        self.base = "\(ip):60606"
        let cfg = URLSessionConfiguration.ephemeral
        cfg.timeoutIntervalForRequest = 15
        cfg.timeoutIntervalForResource = 60
        cfg.requestCachePolicy = .reloadIgnoringLocalCacheData
        self.session = URLSession(configuration: cfg)
    }

    // MARK: Browse

    /// Issue a ContentDirectory#Browse for the given objectID.
    /// `filter` selects which metadata to return; `count` 0 = all.
    func browse(objectID: String = "0",
                flag: String = "BrowseDirectChildren",
                filter: String = "*",
                startingIndex: Int = 0,
                requestedCount: Int = 0) async throws -> [LumixFileItem] {
        let envelope = """
        <?xml version="1.0" encoding="utf-8"?>
        <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
          <s:Body>
            <u:Browse xmlns:u="urn:schemas-upnp-org:service:ContentDirectory:1">
              <s:ObjectID>\(objectID)</s:ObjectID>
              <s:BrowseFlag>\(flag)</s:BrowseFlag>
              <s:Filter>\(filter)</s:Filter>
              <s:StartingIndex>\(startingIndex)</s:StartingIndex>
              <s:RequestedCount>\(requestedCount)</s:RequestedCount>
              <s:SortCriteria></s:SortCriteria>
            </u:Browse>
          </s:Body>
        </s:Envelope>
        """
        guard let url = URL(string: "http://\(base)/Server0/CDS_control") else { throw LumixError.badURL }
        var req = URLRequest(url: url)
        req.httpMethod = "POST"
        req.setValue("text/xml; charset=\"utf-8\"", forHTTPHeaderField: "Content-Type")
        req.setValue("urn:schemas-upnp-org:service:ContentDirectory:1#Browse", forHTTPHeaderField: "SOAPAction")
        req.setValue("Panasonic MIL DLNA CP UPnP/1.0", forHTTPHeaderField: "User-Agent")
        req.setValue(base, forHTTPHeaderField: "Host")
        req.httpBody = envelope.data(using: .utf8)

        let (data, resp) = try await session.data(for: req)
        let status = (resp as? HTTPURLResponse)?.statusCode ?? 0
        guard status == 200 else { throw LumixError.server(status, String(data: data, encoding: .utf8) ?? "") }
        let xml = String(data: data, encoding: .utf8) ?? ""
        return Self.parseItems(xml)
    }

    // MARK: Download

    enum Convert: String {
        case original, medium = "MediumSize", small = "SmallSize"
    }

    /// Download a file (or thumbnail) from a `res` URL.
    func download(resURL: String, convert: Convert = .original) async throws -> (data: Data, size: Int64?) {
        guard let url = URL(string: resURL) else { throw LumixError.badURL }
        var req = URLRequest(url: url)
        req.setValue("Panasonic MIL DLNA CP UPnP/1.0", forHTTPHeaderField: "User-Agent")
        if convert != .original { req.setValue(convert.rawValue, forHTTPHeaderField: "X-CONVERT") }
        let (data, resp) = try await session.data(for: req)
        let http = resp as? HTTPURLResponse
        let sizeStr = http?.value(forHTTPHeaderField: "X-FILE_SIZE")
        let size = sizeStr.flatMap { Int64($0) }
        let status = http?.statusCode ?? 0
        guard status == 200 else { throw LumixError.server(status, "download failed for \(resURL)") }
        return (data, size)
    }

    // MARK: XML item parsing

    static func parseItems(_ xml: String) -> [LumixFileItem] {
        var items: [LumixFileItem] = []
        // Split into item blocks. Panasonic uses <D-Item>; some firmwares use <item>.
        let blockOpen = [ "<D-Item", "<item" ]
        var cursor = xml.startIndex
        while cursor < xml.endIndex {
            var found: (start: String.Index, open: String)? = nil
            for open in blockOpen {
                if let r = xml.range(of: open, range: cursor..<xml.endIndex) {
                    if found == nil || r.lowerBound < found!.start {
                        found = (r.lowerBound, open)
                    }
                }
            }
            guard let f = found else { break }
            let closeTag = f.open == "<D-Item" ? "</D-Item>" : "</item>"
            guard let close = xml.range(of: closeTag, range: f.start..<xml.endIndex) else { break }
            let block = xml[f.start..<close.upperBound]
            items.append(parseBlock(block))
            cursor = close.upperBound
        }
        return items
    }

    private static func parseBlock(_ block: Substring) -> LumixFileItem {
        let s = String(block)
        func attr(_ name: String) -> String {
            // name="value"
            let pat = "\(name)=\""
            guard let a = s.range(of: pat), let b = s.range(of: "\"", range: a.upperBound..<s.endIndex) else { return "" }
            return String(s[a.upperBound..<b.lowerBound])
        }
        func tag(_ name: String) -> String {
            let open = "<\(name)>"
            let close = "</\(name)>"
            guard let a = s.range(of: open), let b = s.range(of: close, range: (a.upperBound)..<s.endIndex), a.lowerBound < b.lowerBound else { return "" }
            return String(s[a.upperBound..<b.lowerBound]).trimmingCharacters(in: .whitespacesAndNewlines)
        }
        let id = attr("id")
        let parent = attr("parentID")
        let cls = attr("upnpclass")
        let title = tag("dc:title")
        var res: String? = nil
        if let a = s.range(of: "<res"), let b = s.range(of: "</res>", range: a.upperBound..<s.endIndex) {
            res = String(s[a.upperBound..<b.lowerBound]).trimmingCharacters(in: .whitespacesAndNewlines)
        }
        let sizeStr = tag("size")
        let size = sizeStr.isEmpty ? nil : Int64(sizeStr)
        return LumixFileItem(id: id.isEmpty ? title : id,
                              parentID: parent,
                              title: title,
                              upnpClass: cls,
                              res: res,
                              size: size)
    }
 }

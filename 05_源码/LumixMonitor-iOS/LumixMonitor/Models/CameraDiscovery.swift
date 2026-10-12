// CameraDiscovery.swift
//
// Discovers Lumix cameras on the local network.
//   1. Bonjour (NetServiceBrowser) for "_http._tcp." services.
//   2. Manual IP entry, validated with a `getstate` probe.
//
// The browser's delegate callbacks arrive on a background thread, so we keep a
// small nonisolated `Browser` object that owns the NetServiceBrowser and only
// forwards resolved (Sendable) values back to the @MainActor model.
//
import Foundation
import Combine

@MainActor
final class CameraDiscovery: ObservableObject {

    @Published var found: [NetServiceFound] = []
    @Published var isBrowsing = false

    struct NetServiceFound: Identifiable, Equatable, Sendable {
        let id: String
        let name: String
        let host: String
        let port: Int
    }

    private var browser: Browser?

    func startBrowsing() {
        guard browser == nil else { return }
        isBrowsing = true
        let b = Browser(
            onFound: { [weak self] item in
                Task { @MainActor in self?.appendFound(item) }
            },
            onFailed: { [weak self] in
                Task { @MainActor in self?.isBrowsing = false }
            }
        )
        b.start()
        browser = b
    }

    func stopBrowsing() {
        browser?.stop()
        browser = nil
        found = []
        isBrowsing = false
    }

    private func appendFound(_ item: NetServiceFound) {
        guard !found.contains(where: { $0.id == item.id }) else { return }
        found.append(item)
    }

    /// Validate a manual IP by probing `getstate`.
    func probe(_ ip: String) async -> CameraState? {
        let client = LumixClient(ip: ip)
        do { return try await client.getstate() }
        catch { return nil }
    }
}

/// Background-thread delegate that owns the NetServiceBrowser and the resolved
/// NetServices. It never touches MainActor state; it only forwards Sendable values.
private final class Browser: NSObject, NetServiceBrowserDelegate, NetServiceDelegate {
    private let onFound: (CameraDiscovery.NetServiceFound) -> Void
    private let onFailed: () -> Void
    private var browser: NetServiceBrowser?
    private var services: [NetService] = []

    init(onFound: @escaping (CameraDiscovery.NetServiceFound) -> Void,
         onFailed: @escaping () -> Void) {
        self.onFound = onFound
        self.onFailed = onFailed
    }

    func start() {
        let b = NetServiceBrowser()
        b.delegate = self
        b.searchForServices(ofType: "_http._tcp.", inDomain: "")
        browser = b
    }

    func stop() {
        browser?.stop()
        browser = nil
        services.forEach { $0.stop() }
        services.removeAll()
    }

    // MARK: NetServiceBrowserDelegate

    func netServiceBrowser(_ browser: NetServiceBrowser, didNotSearch error: [String: NSNumber]) {
        onFailed()
    }

    func netServiceBrowser(_ browser: NetServiceBrowser, didFind service: NetService, moreComing: Bool) {
        service.delegate = self
        service.resolve(withTimeout: 3)
        services.append(service)
    }

    func netServiceBrowser(_ browser: NetServiceBrowser, didRemove service: NetService, moreComing: Bool) {}

    // MARK: NetServiceDelegate

    func netService(_ sender: NetService, didUpdateTXTRecord data: Data) {}

    func netServiceDidResolveAddress(_ sender: NetService) {
        guard let addr = sender.addresses?.first,
              let host = Browser.ipString(from: addr) else { return }
        let item = CameraDiscovery.NetServiceFound(
            id: "\(host):\(sender.port)",
            name: sender.name,
            host: host,
            port: sender.port)
        onFound(item)
    }

    /// Convert a resolved `sockaddr` (as Data) into an IPv4/IPv6 address string.
    static func ipString(from data: Data) -> String? {
        return data.withUnsafeBytes { (raw: UnsafeRawBufferPointer) -> String? in
            guard let saPtr = raw.bindMemory(to: sockaddr.self).baseAddress else { return nil }
            switch saPtr.pointee.sa_family {
            case UInt8(AF_INET):
                guard let sa4 = raw.bindMemory(to: sockaddr_in.self).baseAddress,
                      raw.count >= MemoryLayout<sockaddr_in>.size else { return nil }
                var addr = sa4.pointee.sin_addr
                var buf = [CChar](repeating: 0, count: Int(INET_ADDRSTRLEN))
                guard inet_ntop(AF_INET, &addr, &buf, socklen_t(INET_ADDRSTRLEN)) != nil else { return nil }
                return String(cString: buf)
            case UInt8(AF_INET6):
                guard let sa6 = raw.bindMemory(to: sockaddr_in6.self).baseAddress,
                      raw.count >= MemoryLayout<sockaddr_in6>.size else { return nil }
                var addr = sa6.pointee.sin6_addr
                var buf = [CChar](repeating: 0, count: Int(INET6_ADDRSTRLEN))
                guard inet_ntop(AF_INET6, &addr, &buf, socklen_t(INET6_ADDRSTRLEN)) != nil else { return nil }
                return String(cString: buf)
            default:
                return nil
            }
        }
    }

    func netService(_ sender: NetService, didNotResolve error: [String: NSNumber]) {}
}

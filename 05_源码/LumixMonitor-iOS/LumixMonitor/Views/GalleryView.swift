// GalleryView.swift
//
// Camera media browser via DLNA (port 60606). Navigate containers,
// preview thumbnails (X-CONVERT: SmallSize), download originals to Photos.
//
import SwiftUI

struct GalleryView: View {
    @EnvironmentObject var model: AppModel
    @State private var selected: LumixFileItem?

    var body: some View {
        Group {
            if model.files.isEmpty {
                emptyState
            } else {
                List {
                    if model.browsingPath.count > 0 {
                        Button {
                            model.goUp()
                        } label: {
                            Label("上级目录", systemImage: "arrow.up")
                        }
                        .listRowBackground(Color.clear)
                    }
                    ForEach(model.files) { item in
                        fileRow(item)
                    }
                }
                .listStyle(.insetGrouped)
            }
        }
        .navigationTitle(title)
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                Button {
                    Task { await model.loadGallery() }
                } label: {
                    Image(systemName: "arrow.clockwise")
                }
                .disabled(model.galleryBusy || model.downloading)
            }
        }
        .onAppear {
            if model.files.isEmpty { Task { await model.loadGallery() } }
        }
        .sheet(item: $selected) { item in
            if item.isMedia {
                DownloadSheet(item: item)
            }
        }
    }

    private var title: String {
        model.browsingPath.isEmpty ? "相机相册" : model.browsingPath.last?.title ?? "相机相册"
    }

    private var emptyState: some View {
        VStack(spacing: 10) {
            if model.downloading || model.galleryBusy {
                ProgressView()
                Text("正在加载…").font(.footnote)
            } else {
                Image(systemName: "photo.on.rectangle.angled")
                    .font(.system(size: 40))
                    .foregroundStyle(.secondary)
                Text("没有内容").font(.footnote).foregroundStyle(.secondary)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }

    private func fileRow(_ item: LumixFileItem) -> some View {
        Button {
            if item.isContainer {
                Task { await model.openContainer(item) }
            } else if item.isMedia {
                selected = item
            }
        } label: {
            HStack(spacing: 12) {
                if item.isMedia, let thumb = model.thumbnailCache[item.id] {
                    Image(uiImage: thumb)
                        .resizable()
                        .aspectRatio(contentMode: .fill)
                        .frame(width: 44, height: 44)
                        .clipShape(RoundedRectangle(cornerRadius: 6))
                } else {
                    Image(systemName: item.isContainer ? "folder" : "photo")
                        .font(.title3)
                        .foregroundStyle(item.isContainer ? .orange : .cyan)
                        .frame(width: 44, height: 44)
                }
                VStack(alignment: .leading, spacing: 2) {
                    Text(item.title).font(.body)
                    if let size = item.size, item.isMedia {
                        Text(bytes(size)).font(.caption).foregroundStyle(.secondary)
                    }
                }
                Spacer()
                if item.isContainer {
                    Image(systemName: "chevron.right").font(.caption).foregroundStyle(.secondary)
                }
            }
        }
    }

    private func bytes(_ n: Int64) -> String {
        let units = ["B", "KB", "MB", "GB"]
        var v = Double(n); var i = 0
        while v >= 1024 && i < units.count - 1 { v /= 1024; i += 1 }
        return String(format: "%.1f %@", v, units[i])
    }
}

// MARK: - Download sheet

private struct DownloadSheet: View {
    @EnvironmentObject var model: AppModel
    @Environment(\.dismiss) private var dismiss
    let item: LumixFileItem
    @State private var busy = false

    var body: some View {
        VStack(spacing: 16) {
            if let thumb = model.thumbnailCache[item.id] {
                Image(uiImage: thumb)
                    .resizable()
                    .aspectRatio(contentMode: .fit)
                    .frame(maxHeight: 220)
                    .clipShape(RoundedRectangle(cornerRadius: 8))
            }
            Text("下载照片").font(.headline)
            Text(item.title).font(.subheadline).foregroundStyle(.secondary)
            if let size = item.size {
                Text(bytes(size)).font(.caption).foregroundStyle(.tertiary)
            }
            if busy {
                ProgressView()
                Text("正在通过 DLNA 下载…").font(.caption).foregroundStyle(.secondary)
            } else {
                Button {
                    busy = true
                    Task {
                        await model.download(item)
                        busy = false
                        dismiss()
                    }
                } label: {
                    Label("保存到相册", systemImage: "arrow.down.circle")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.borderedProminent)
            }
            Button("取消") { dismiss() }
                .font(.footnote)
        }
        .padding()
        .presentationDetents([.medium])
    }

    private func bytes(_ n: Int64) -> String {
        let units = ["B", "KB", "MB", "GB"]
        var v = Double(n); var i = 0
        while v >= 1024 && i < units.count - 1 { v /= 1024; i += 1 }
        return String(format: "%.1f %@", v, units[i])
    }
}

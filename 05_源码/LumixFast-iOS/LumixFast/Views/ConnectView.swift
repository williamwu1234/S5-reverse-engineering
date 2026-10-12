 // ConnectView.swift
 import SwiftUI

 struct ConnectView: View {
     @EnvironmentObject var model: AppModel
     @StateObject private var discovery = CameraDiscovery()
     @State private var manualIP: String = ""
     @State private var showManual = false

     var body: some View {
         NavigationStack {
             ScrollView {
                 VStack(spacing: 20) {
                     header
                     permissionCard
                     manualCard
                     discoveredCard
                 }
                 .padding()
             }
             .background(Color.black.ignoresSafeArea())
             .navigationTitle("Lumix Fast")
             .onAppear {
                 discovery.startBrowsing()
                 Task { await model.requestPhotoPermission() }
             }
             .onDisappear { discovery.stopBrowsing() }
         }
     }

     private var header: some View {
         VStack(spacing: 6) {
             Image(systemName: "camera.aperture")
                 .font(.system(size: 46))
                 .foregroundStyle(.cyan)
             Text("LUMIX 遥控 / 联机")
                 .font(.title3.weight(.semibold))
             Text("通过 Wi-Fi 连接相机，实现取景、快门与照片回传。全程本地运行，无云端。")
                 .font(.footnote)
                 .foregroundStyle(.secondary)
                 .multilineTextAlignment(.center)
         }
         .frame(maxWidth: .infinity)
         .padding(.vertical, 12)
     }

     private var permissionCard: some View {
         Button {
             Task { await model.requestPhotoPermission() }
         } label: {
             Label("授权相册（用于保存回传的照片）", systemImage: "photo.badge.plus")
                 .frame(maxWidth: .infinity)
         }
         .buttonStyle(.bordered)
     }

     private var manualCard: some View {
         VStack(alignment: .leading, spacing: 10) {
             Text("手动输入相机 IP").font(.headline)
             HStack {
                 TextField("192.168.x.x", text: $manualIP)
                     .keyboardType(.numbersAndPunctuation)
                     .textInputAutocapitalization(.never)
                     .autocorrectionDisabled()
                     .padding(8)
                     .background(Color(.systemGray6))
                     .clipShape(RoundedRectangle(cornerRadius: 8))
                 Button("连接") {
                     Task { await model.connect(ip: manualIP) }
                 }
                 .buttonStyle(.borderedProminent)
                 .disabled(manualIP.trimmingCharacters(in: .whitespaces).isEmpty || model.isConnecting)
             }
             if model.isConnecting {
                 HStack(spacing: 8) {
                     ProgressView()
                     Text(model.statusMessage).font(.caption).foregroundStyle(.secondary)
                 }
             }
             if !model.errorMessage.isEmpty {
                 Text(model.errorMessage).font(.caption).foregroundStyle(.red)
             }
         }
         .padding()
         .background(Color(.systemGray5))
         .clipShape(RoundedRectangle(cornerRadius: 12))
     }

     private var discoveredCard: some View {
         VStack(alignment: .leading, spacing: 10) {
             HStack {
                 Text("自动发现（Bonjour）").font(.headline)
                 Spacer()
                 if discovery.isBrowsing { ProgressView() }
             }
             if discovery.found.isEmpty {
                 Text("未发现相机。请确认相机已开启 Wi-Fi 并与手机在同一网络。")
                     .font(.caption).foregroundStyle(.secondary)
             } else {
                 ForEach(discovery.found) { item in
                     Button {
                         Task { await model.connect(ip: item.host) }
                     } label: {
                         HStack {
                             Image(systemName: "camera")
                             VStack(alignment: .leading) {
                                 Text(item.name).font(.body.weight(.medium))
                                 Text("\(item.host):\(item.port)").font(.caption).foregroundStyle(.secondary)
                             }
                             Spacer()
                             Image(systemName: "chevron.right").font(.caption).foregroundStyle(.secondary)
                         }
                         .padding(.vertical, 6)
                     }
                     .foregroundStyle(.primary)
                 }
             }
         }
         .padding()
         .background(Color(.systemGray5))
         .clipShape(RoundedRectangle(cornerRadius: 12))
     }
 }

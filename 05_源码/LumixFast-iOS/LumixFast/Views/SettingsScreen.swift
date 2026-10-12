 // SettingsScreen.swift
 //
 // Camera settings (photo style) and connection controls.
 //
 import SwiftUI

 struct SettingsScreen: View {
     @EnvironmentObject var model: AppModel
     @State private var currentStyle: String = "STANDARD"

     var body: some View {
         NavigationStack {
             Form {
                Section {
                    Picker("照片风格", selection: $currentStyle) {
                        ForEach(model.photoStyles, id: \.self) { s in
                            Text(s).tag(s)
                        }
                    }
                    .pickerStyle(.menu)
                    .onChange(of: currentStyle) { _, newValue in
                        Task { await model.setPhotoStyle(newValue) }
                    }
                } header: {
                    Text("拍摄设置")
                } footer: {
                    Text("通过 cam.cgi setsetting 写入机内照片风格。")
                }

                Section {
                    LabeledContent("相机地址", value: model.ip)
                    LabeledContent("固件", value: model.state?.version ?? "-")
                    LabeledContent("模式", value: model.state?.camMode ?? "-")
                } header: {
                    Text("连接信息")
                }

                Section {
                    Button("断开连接", role: .destructive) {
                        model.disconnect()
                    }
                }
             }
             .navigationTitle("设置")
         }
     }
 }

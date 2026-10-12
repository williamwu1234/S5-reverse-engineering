 // RootView.swift
 //
 // Top-level navigation. When not connected, shows the connect screen.
 // When connected, tabs: 取景 (Live View), 相册 (Gallery), 设置 (Settings).
 //
 import SwiftUI

 struct RootView: View {
     @EnvironmentObject var model: AppModel

     var body: some View {
         Group {
             if model.isConnected {
                 connectedTabs
             } else {
                 ConnectView()
             }
         }
     }

     private var connectedTabs: some View {
         TabView {
             LiveViewScreen()
                 .tabItem { Label("取景", systemImage: "video") }
             GalleryView()
                 .tabItem { Label("相册", systemImage: "photo.on.rectangle.angled") }
             SettingsScreen()
                 .tabItem { Label("设置", systemImage: "slider.horizontal.3") }
         }
     }
 }

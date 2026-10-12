 // LumixFastApp.swift
 import SwiftUI

 @main
 struct LumixFastApp: App {
     @StateObject private var model = AppModel()

     var body: some Scene {
         WindowGroup {
             RootView()
                 .environmentObject(model)
                 .preferredColorScheme(.dark)
                 .tint(.cyan)
         }
     }
 }

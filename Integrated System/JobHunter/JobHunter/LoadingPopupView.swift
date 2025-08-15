import SwiftUI

struct LoadingPopupView: View {
    var body: some View {
        ZStack {
            Color.black.opacity(0.4)
                .edgesIgnoringSafeArea(.all)
            VStack(spacing: 24) {
                // Loading GIF
                if let url = Bundle.main.url(forResource: "loading", withExtension: "gif") {
                    GIFView(gifURL: url)
                        .frame(width: 80, height: 80)
                } else {
                    ProgressView()
                        .scaleEffect(2)
                }
                Text("Please wait up to 5 minutes while jobs are being fetched...")
                    .font(.headline)
                    .foregroundColor(.white)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal)
            }
            .padding(32)
            .background(Color(.systemGray6))
            .cornerRadius(16)
            .shadow(radius: 12)
        }
    }
}

// GIFView implementation using WebKit
import WebKit
struct GIFView: UIViewRepresentable {
    let gifURL: URL
    func makeUIView(context: Context) -> WKWebView {
        let webView = WKWebView()
        webView.isOpaque = false
        webView.backgroundColor = .clear
        webView.scrollView.isScrollEnabled = false
        let html = """
        <html><body style='margin:0;background:transparent;'>
        <img src='\(gifURL.absoluteString)' style='width:100%;height:100%;object-fit:contain;' />
        </body></html>
        """
        webView.loadHTMLString(html, baseURL: nil)
        return webView
    }
    func updateUIView(_ uiView: WKWebView, context: Context) {}
}

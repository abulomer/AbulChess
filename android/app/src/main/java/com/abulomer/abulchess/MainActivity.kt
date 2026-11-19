package com.abulomer.abulchess

import android.app.Activity
import android.app.AlertDialog
import android.content.ActivityNotFoundException
import android.content.Intent
import android.graphics.Color
import android.net.Uri
import android.os.Bundle
import android.view.Gravity
import android.view.View
import android.view.ViewGroup
import android.webkit.WebChromeClient
import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.ProgressBar
import android.widget.TextView
import android.widget.Toast

class MainActivity : Activity() {
    private lateinit var webView: WebView
    private lateinit var progress: ProgressBar
    private lateinit var message: TextView
    private var serverUri: Uri? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        buildLayout()
        configureWebView()

        val savedAddress = getPreferences(MODE_PRIVATE).getString(SERVER_ADDRESS_KEY, null)
        if (savedAddress == null) {
            webView.post { showServerDialog("") }
        } else {
            loadServer(savedAddress)
        }
    }

    private fun buildLayout() {
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(Color.rgb(11, 16, 32))
        }
        val toolbar = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
            setPadding(dp(16), dp(8), dp(12), dp(8))
        }
        val title = TextView(this).apply {
            text = "AbulChess"
            textSize = 18f
            setTextColor(Color.WHITE)
        }
        val changeServer = Button(this).apply {
            text = "Sunucu adresi"
            setOnClickListener { showServerDialog(serverUri?.toString().orEmpty()) }
        }
        toolbar.addView(title, LinearLayout.LayoutParams(0, dp(48), 1f))
        toolbar.addView(changeServer, LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.WRAP_CONTENT,
            dp(48)
        ))

        progress = ProgressBar(this, null, android.R.attr.progressBarStyleHorizontal).apply {
            isIndeterminate = true
            visibility = View.GONE
        }
        message = TextView(this).apply {
            gravity = Gravity.CENTER
            textSize = 16f
            setTextColor(Color.WHITE)
            visibility = View.GONE
        }
        webView = WebView(this)

        root.addView(toolbar)
        root.addView(progress, LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            dp(3)
        ))
        root.addView(message, LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            0,
            1f
        ))
        root.addView(webView, LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            0,
            1f
        ))
        setContentView(root)
    }

    private fun configureWebView() {
        webView.settings.javaScriptEnabled = true
        webView.settings.domStorageEnabled = true
        webView.settings.allowFileAccess = false
        webView.settings.allowContentAccess = false
        webView.webChromeClient = WebChromeClient()
        webView.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(
                view: WebView,
                request: WebResourceRequest
            ): Boolean {
                val destination = request.url
                val current = serverUri ?: return true
                if (destination.scheme == current.scheme &&
                    destination.host == current.host &&
                    destination.port == current.port
                ) {
                    return false
                }
                if (destination.scheme == "http" || destination.scheme == "https") {
                    try {
                        startActivity(Intent(Intent.ACTION_VIEW, destination))
                    } catch (_: ActivityNotFoundException) {
                        Toast.makeText(this@MainActivity, "Bağlantı açılamadı", Toast.LENGTH_SHORT).show()
                    }
                }
                return true
            }

            override fun onPageStarted(view: WebView, url: String, favicon: android.graphics.Bitmap?) {
                progress.visibility = View.VISIBLE
                message.visibility = View.GONE
                webView.visibility = View.VISIBLE
            }

            override fun onPageFinished(view: WebView, url: String) {
                progress.visibility = View.GONE
            }

            override fun onReceivedError(
                view: WebView,
                request: WebResourceRequest,
                error: android.webkit.WebResourceError
            ) {
                if (request.isForMainFrame) {
                    progress.visibility = View.GONE
                    webView.visibility = View.GONE
                    message.text = "Sunucuya bağlanılamadı.\nAynı Wi-Fi ağında olduğunuzu ve sunucunun çalıştığını kontrol edin."
                    message.visibility = View.VISIBLE
                }
            }
        }
    }

    private fun showServerDialog(initialAddress: String) {
        val input = EditText(this).apply {
            hint = "192.168.1.10:8765"
            setSingleLine(true)
            setText(initialAddress)
            setSelection(text.length)
            setPadding(dp(20), dp(8), dp(20), dp(8))
        }
        val dialog = AlertDialog.Builder(this)
            .setTitle("LAN sunucusuna bağlan")
            .setMessage("Bilgisayarda Satranç Pro çalışırken görünen yerel ağ adresini girin.")
            .setView(input)
            .setPositiveButton("Bağlan", null)
            .setNegativeButton("İptal", null)
            .create()
        dialog.setOnShowListener {
            dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener {
                val normalized = normalizeAddress(input.text.toString())
                if (normalized == null) {
                    input.error = "IP:port veya http://adres:port girin"
                    return@setOnClickListener
                }
                getPreferences(MODE_PRIVATE).edit()
                    .putString(SERVER_ADDRESS_KEY, normalized)
                    .apply()
                dialog.dismiss()
                loadServer(normalized)
            }
        }
        dialog.show()
    }

    private fun normalizeAddress(value: String): String? {
        val trimmed = value.trim().trimEnd('/')
        if (trimmed.isEmpty()) return null
        val withScheme = if (trimmed.startsWith("http://", true) ||
            trimmed.startsWith("https://", true)
        ) trimmed else "http://$trimmed"
        val uri = Uri.parse(withScheme)
        val port = uri.port
        if ((uri.scheme != "http" && uri.scheme != "https") ||
            uri.host.isNullOrBlank() ||
            uri.userInfo != null ||
            (!uri.path.isNullOrEmpty() && uri.path != "/") ||
            uri.query != null ||
            uri.fragment != null ||
            (port != -1 && port !in 1..65535)
        ) {
            return null
        }
        return uri.buildUpon().path("").build().toString().trimEnd('/')
    }

    private fun loadServer(address: String) {
        val normalized = normalizeAddress(address) ?: run {
            showServerDialog("")
            return
        }
        serverUri = Uri.parse(normalized)
        message.visibility = View.GONE
        webView.visibility = View.VISIBLE
        webView.loadUrl(normalized)
    }

    override fun onBackPressed() {
        if (::webView.isInitialized && webView.canGoBack()) {
            webView.goBack()
        } else {
            super.onBackPressed()
        }
    }

    override fun onPause() {
        if (::webView.isInitialized) webView.onPause()
        super.onPause()
    }

    override fun onResume() {
        super.onResume()
        if (::webView.isInitialized) webView.onResume()
    }

    override fun onDestroy() {
        if (::webView.isInitialized) {
            webView.stopLoading()
            webView.destroy()
        }
        super.onDestroy()
    }

    private fun dp(value: Int): Int = (value * resources.displayMetrics.density).toInt()

    companion object {
        private const val SERVER_ADDRESS_KEY = "server_address"
    }
}

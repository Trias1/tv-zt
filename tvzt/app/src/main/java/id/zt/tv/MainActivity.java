package id.zt.tv;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.net.Uri;
import android.webkit.ValueCallback;
import android.content.res.ColorStateList;
import android.graphics.Typeface;
import android.os.Bundle;
import android.text.SpannableString;
import android.text.style.ForegroundColorSpan;
import android.util.TypedValue;
import android.view.Gravity;
import android.view.ViewGroup;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.view.KeyEvent;
import android.view.View;
import android.view.WindowManager;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * TV ZT: satu layar WebView yang memuat tampilan HTML (assets/index.html).
 * Sisi Java mengurus hal yang tidak boleh dilakukan halaman web:
 *  - membaca playlist dari folder aplikasi (bisa diganti lewat adb push tanpa izin penyimpanan),
 *  - mengirim header Referer/User-Agent khusus untuk channel yang memintanya (RCTI, GTV, Trans resmi),
 *  - meneruskan tombol remote ke halaman, dan menutup aplikasi saat Back ditekan di beranda.
 */
public class MainActivity extends Activity {

    private WebView web;
    /** Header untuk channel yang sedang diputar; kosong = biarkan WebView memuat sendiri. */
    private volatile String referer = "";
    private volatile String userAgent = "";
    private static final int PILIH_FILE = 7;
    private View splash;
    private ValueCallback<Uri[]> fileCallback;

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);

        web = new WebView(this);
        web.setBackgroundColor(0xFF0A1220);
        // Layar pembuka bawaan Android: tampil seketika selagi halaman (± 1,3 MB data channel) dimuat,
        // ditutup saat halaman memanggil Android.siap() (atau paling lambat 20 detik).
        FrameLayout root = new FrameLayout(this);
        root.addView(web, new FrameLayout.LayoutParams(FrameLayout.LayoutParams.MATCH_PARENT, FrameLayout.LayoutParams.MATCH_PARENT));
        splash = buatSplash();
        root.addView(splash, new FrameLayout.LayoutParams(FrameLayout.LayoutParams.MATCH_PARENT, FrameLayout.LayoutParams.MATCH_PARENT));
        setContentView(root);
        web.postDelayed(this::tutupSplash, 20000);
        hideSystemBars();

        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setMediaPlaybackRequiresUserGesture(false);
        s.setAllowFileAccess(true);
        // Halaman dimuat dari file:///android_asset; izin ini membuat permintaan stream tidak tertahan CORS.
        s.setAllowFileAccessFromFileURLs(true);
        s.setAllowUniversalAccessFromFileURLs(true);
        s.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);
        // Cache biasa: logo channel cukup diunduh sekali. Playlist siaran langsung tetap segar karena servernya
        // mengirim header no-cache, dan channel ber-header khusus lewat intercept() tanpa cache.
        s.setCacheMode(WebSettings.LOAD_DEFAULT);
        WebView.setWebContentsDebuggingEnabled(true);

        web.addJavascriptInterface(new Bridge(), "Android");
        web.setWebChromeClient(new WebChromeClient() {
            // "Playlist saya → Tambah dari file": buka pemilih file (mis. File Manager+) untuk .m3u.
            @Override
            public boolean onShowFileChooser(WebView view, ValueCallback<Uri[]> cb, FileChooserParams params) {
                if (fileCallback != null) fileCallback.onReceiveValue(null);
                fileCallback = cb;
                Intent i = new Intent(Intent.ACTION_GET_CONTENT).addCategory(Intent.CATEGORY_OPENABLE).setType("*/*");
                try {
                    startActivityForResult(Intent.createChooser(i, "Pilih file playlist"), PILIH_FILE);
                } catch (ActivityNotFoundException e) {
                    fileCallback = null;
                    cb.onReceiveValue(null);
                    return false;
                }
                return true;
            }
        });
        web.setWebViewClient(new WebViewClient() {
            @Override
            public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest req) {
                return intercept(req);
            }
        });
        web.loadUrl("file:///android_asset/index.html");
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode != PILIH_FILE || fileCallback == null) return;
        Uri u = resultCode == RESULT_OK && data != null ? data.getData() : null;
        fileCallback.onReceiveValue(u == null ? null : new Uri[]{u});
        fileCallback = null;
    }

    private void hideSystemBars() {
        getWindow().getDecorView().setSystemUiVisibility(
                View.SYSTEM_UI_FLAG_FULLSCREEN | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                        | View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY | View.SYSTEM_UI_FLAG_LAYOUT_STABLE);
    }

    /* ---------------- remote ---------------- */

    @Override
    public boolean dispatchKeyEvent(KeyEvent e) {
        String k = keyName(e.getKeyCode());
        if (k == null) return super.dispatchKeyEvent(e);
        if (e.getAction() == KeyEvent.ACTION_DOWN) {
            final boolean isBack = k.equals("back");
            web.evaluateJavascript("window.TVZT ? TVZT.key('" + k + "') : true", result -> {
                if (isBack && "false".equals(result)) finish();
            });
        }
        return true; // dipakai sepenuhnya, supaya WebView tidak ikut menggulir atau berpindah fokus
    }

    private static String keyName(int code) {
        switch (code) {
            case KeyEvent.KEYCODE_DPAD_UP: return "up";
            case KeyEvent.KEYCODE_DPAD_DOWN: return "down";
            case KeyEvent.KEYCODE_DPAD_LEFT: return "left";
            case KeyEvent.KEYCODE_DPAD_RIGHT: return "right";
            case KeyEvent.KEYCODE_DPAD_CENTER:
            case KeyEvent.KEYCODE_ENTER:
            case KeyEvent.KEYCODE_NUMPAD_ENTER: return "ok";
            case KeyEvent.KEYCODE_BACK:
            case KeyEvent.KEYCODE_ESCAPE: return "back";
            case KeyEvent.KEYCODE_MENU: return "menu";
            case KeyEvent.KEYCODE_CHANNEL_UP:
            case KeyEvent.KEYCODE_PAGE_UP: return "chup";
            case KeyEvent.KEYCODE_CHANNEL_DOWN:
            case KeyEvent.KEYCODE_PAGE_DOWN: return "chdown";
            default: return null;
        }
    }

    /* ---------------- header khusus ---------------- */

    private WebResourceResponse intercept(WebResourceRequest req) {
        String ref = referer, ua = userAgent;
        String url = req.getUrl().toString();
        if ((ref.isEmpty() && ua.isEmpty()) || !"GET".equals(req.getMethod()) || !url.startsWith("http")) return null;
        String host = req.getUrl().getHost();
        if (host == null || host.contains("googleapis.com") || host.contains("gstatic.com")) return null;
        try {
            HttpURLConnection c = null;
            for (int hop = 0; hop < 5; hop++) {
                c = (HttpURLConnection) new URL(url).openConnection();
                c.setInstanceFollowRedirects(false);
                c.setConnectTimeout(10000);
                c.setReadTimeout(15000);
                for (Map.Entry<String, String> h : req.getRequestHeaders().entrySet()) {
                    String n = h.getKey();
                    // Accept-Encoding dilewati: HttpURLConnection membuka gzip sendiri hanya kalau ia yang memintanya.
                    if (n.equalsIgnoreCase("Referer") || n.equalsIgnoreCase("User-Agent") || n.equalsIgnoreCase("Origin")
                            || n.equalsIgnoreCase("Accept-Encoding")) continue;
                    c.setRequestProperty(n, h.getValue());
                }
                if (!ref.isEmpty()) c.setRequestProperty("Referer", ref);
                if (!ua.isEmpty()) c.setRequestProperty("User-Agent", ua);
                int code = c.getResponseCode();
                if (code >= 300 && code < 400 && c.getHeaderField("Location") != null) {
                    url = new URL(new URL(url), c.getHeaderField("Location")).toString();
                    c.disconnect();
                    continue;
                }
                break;
            }
            int code = c.getResponseCode();
            String reason = c.getResponseMessage();
            if (reason == null || reason.isEmpty()) reason = code < 400 ? "OK" : "Error";
            String type = c.getContentType();
            String mime = type == null ? "application/octet-stream" : type.split(";")[0].trim();
            InputStream body = code < 400 ? c.getInputStream() : c.getErrorStream();
            if (body == null) body = new ByteArrayInputStream(new byte[0]);
            Map<String, String> out = new HashMap<>();
            for (Map.Entry<String, List<String>> h : c.getHeaderFields().entrySet()) {
                if (h.getKey() == null || h.getValue().isEmpty()) continue;
                String n = h.getKey().toLowerCase(Locale.ROOT);
                if (n.startsWith("access-control-") || n.equals("content-encoding") || n.equals("transfer-encoding")) continue;
                out.put(h.getKey(), h.getValue().get(0));
            }
            out.put("Access-Control-Allow-Origin", "*");
            if (code >= 300 && code < 400) code = 502; // WebResourceResponse tidak menerima kode 3xx
            return new WebResourceResponse(mime, null, code, reason, out, body);
        } catch (Exception ex) {
            return null; // biarkan WebView mencoba sendiri; error-nya tampil di layar TV ZT
        }
    }

    /* ---------------- jembatan ke halaman ---------------- */

    private File playlistFile() {
        File dir = getExternalFilesDir(null);
        return dir == null ? null : new File(dir, "playlist.m3u");
    }

    private View buatSplash() {
        float dp = getResources().getDisplayMetrics().density;
        LinearLayout box = new LinearLayout(this);
        box.setOrientation(LinearLayout.VERTICAL);
        box.setGravity(Gravity.CENTER);
        box.setBackgroundColor(0xFF0A1220);
        TextView logo = new TextView(this);
        SpannableString t = new SpannableString("TV ZT");
        t.setSpan(new ForegroundColorSpan(0xFFF4B740), 3, 5, 0);
        logo.setText(t);
        logo.setTextColor(0xFFEEF2F8);
        logo.setTextSize(TypedValue.COMPLEX_UNIT_SP, 56);
        logo.setTypeface(Typeface.create("sans-serif-condensed", Typeface.BOLD));
        logo.setGravity(Gravity.CENTER);
        box.addView(logo, new LinearLayout.LayoutParams(LinearLayout.LayoutParams.WRAP_CONTENT, LinearLayout.LayoutParams.WRAP_CONTENT));
        ProgressBar pb = new ProgressBar(this);
        pb.setIndeterminateTintList(ColorStateList.valueOf(0xFFF4B740));
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams((int) (44 * dp), (int) (44 * dp));
        lp.topMargin = (int) (22 * dp);
        box.addView(pb, lp);
        TextView msg = new TextView(this);
        // Bahasa perangkat Indonesia ("in"/"id") → teks Indonesia, selain itu English.
        String bhs = Locale.getDefault().getLanguage();
        msg.setText("in".equals(bhs) || "id".equals(bhs) ? "Memuat channel…" : "Loading channels…");
        msg.setTextColor(0xFFA3B1C6);
        msg.setTextSize(TypedValue.COMPLEX_UNIT_SP, 16);
        LinearLayout.LayoutParams mp = new LinearLayout.LayoutParams(LinearLayout.LayoutParams.WRAP_CONTENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        mp.topMargin = (int) (16 * dp);
        box.addView(msg, mp);
        return box;
    }

    private void tutupSplash() {
        final View s = splash;
        if (s == null) return;
        splash = null;
        s.animate().alpha(0f).setDuration(350).withEndAction(() -> ((ViewGroup) s.getParent()).removeView(s)).start();
    }

    /** Pemeriksa "Cari sinyal": 6 sekaligus, di luar thread tampilan. */
    private final ExecutorService pemeriksa = Executors.newFixedThreadPool(6);

    /** true kalau link membalas 200 dan isinya playlist HLS (#EXTM3U); mengikuti redirect sampai 5 kali. */
    private static boolean adaSinyal(String url, String ref, String ua) {
        try {
            for (int i = 0; i < 5; i++) {
                HttpURLConnection c = (HttpURLConnection) new URL(url).openConnection();
                c.setConnectTimeout(8000);
                c.setReadTimeout(8000);
                c.setInstanceFollowRedirects(false);
                if (!ref.isEmpty()) c.setRequestProperty("Referer", ref);
                c.setRequestProperty("User-Agent", ua.isEmpty() ? "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 Chrome/120 Mobile Safari/537.36" : ua);
                int code = c.getResponseCode();
                if (code >= 300 && code < 400 && c.getHeaderField("Location") != null) {
                    url = new URL(new URL(url), c.getHeaderField("Location")).toString();
                    c.disconnect();
                    continue;
                }
                if (code != 200) { c.disconnect(); return false; }
                InputStream in = c.getInputStream();
                byte[] b = new byte[512];
                int n = in.read(b);
                in.close();
                c.disconnect();
                String s = n > 0 ? new String(b, 0, n, StandardCharsets.UTF_8).replace("﻿", "").trim() : "";
                return s.startsWith("#EXTM3U");
            }
        } catch (Exception ignored) {
        }
        return false;
    }

    private class Bridge {
        @JavascriptInterface
        public void siap() {
            runOnUiThread(MainActivity.this::tutupSplash);
        }

        @JavascriptInterface
        public void cekSinyal(String id, String url, String ref, String ua) {
            pemeriksa.execute(() -> {
                boolean ok = adaSinyal(url, ref == null ? "" : ref, ua == null ? "" : ua);
                String js = "window.TVZT_SINYAL && TVZT_SINYAL('" + id.replaceAll("[^0-9]", "") + "'," + ok + ")";
                runOnUiThread(() -> web.evaluateJavascript(js, null));
            });
        }

        @JavascriptInterface
        public String playlistText() {
            try {
                File f = playlistFile();
                InputStream in = (f != null && f.isFile()) ? new FileInputStream(f) : getAssets().open("default.m3u");
                ByteArrayOutputStream buf = new ByteArrayOutputStream();
                byte[] b = new byte[8192];
                for (int n; (n = in.read(b)) > 0; ) buf.write(b, 0, n);
                in.close();
                return buf.toString(StandardCharsets.UTF_8.name());
            } catch (Exception e) {
                return "";
            }
        }

        @JavascriptInterface
        public String playlistName() {
            File f = playlistFile();
            return (f != null && f.isFile()) ? "playlist.m3u" : "bawaan aplikasi";
        }

        @JavascriptInterface
        public String playlistDate() {
            File f = playlistFile();
            long t = (f != null && f.isFile()) ? f.lastModified() : 0;
            return t == 0 ? "" : new SimpleDateFormat("d MMM yyyy HH:mm", new Locale("id", "ID")).format(new Date(t));
        }

        @JavascriptInterface
        public void setHeaders(String ref, String ua) {
            referer = ref == null ? "" : ref;
            userAgent = ua == null ? "" : ua;
        }
    }

    /* ---------------- siklus hidup ---------------- */

    @Override
    protected void onResume() {
        super.onResume();
        hideSystemBars();
        web.onResume();
        web.evaluateJavascript("var v=document.querySelector('video'); if (v) v.play().catch(function(){});", null);
    }

    @Override
    protected void onPause() {
        web.evaluateJavascript("var v=document.querySelector('video'); if (v) v.pause();", null);
        web.onPause();
        super.onPause();
    }

    @Override
    protected void onDestroy() {
        web.destroy();
        super.onDestroy();
    }
}

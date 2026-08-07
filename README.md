# 東北旅繪（家人專用）

靜態行程網站，已用密碼加密後部署到 GitHub Pages。

## 家人怎麼看

1. 打開網站網址  
2. 輸入通行密碼（向行程負責人索取）  
3. 同一分頁工作階段會記住；關閉後需重新輸入

## 自己改行程後怎麼更新

1. 編輯 `_source/index.html`（明文原稿；底線資料夾不會被 GitHub Pages/Jekyll 發布）
2. 確認本機有 `.site-password`（密碼檔，已加入 gitignore）  
3. 執行：

```bash
python scripts/lock_site.py
```

4. 提交並推送：

```bash
git add _source/index.html index.html sw.js images
git commit -m "Update itinerary"
git push
```

## 注意

- GitHub Pages **沒有**伺服器端密碼功能；本站是把 HTML 內容 AES 加密後才公開。  
- 明文原稿必須留在 `_source/`，且不要在倉庫根目錄放 `.nojekyll`（legacy/Jekyll 部署時會發布底線資料夾）。
- 沒有密碼看不到行程內文；但無法防範「已知道密碼的人再轉傳」。  
- 倉庫請維持 **Private**，並只邀請需要一起改行程的家人當 collaborator。

## 部署（GitHub Pages）

建議改用 Actions 部署（可穩定排除 `_source/`，也不依賴 Jekyll）：

1. Repo → **Settings → Pages → Build and deployment → Source** 選 **GitHub Actions**
2. 合併到 `main` 後會跑 `.github/workflows/deploy-pages.yml`；也可在 Actions 手動 **Run workflow**

若 Actions 裡的 `pages build and deployment` 一直卡在 **queued**（legacy 分支部署常見卡鎖）：

1. **Settings → Environments → github-pages** → Deployment history，刪除卡住／進行中的 deployment（釋放 concurrency lock）
2. 或到 **Settings → Pages**，暫時改 Source 路徑／分支後存檔，再改回原設定
3. 再推一次 `main`，或改用上方 **GitHub Actions** 來源後手動 Run workflow

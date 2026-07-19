# 東北旅繪（家人專用）

靜態行程網站，已用密碼加密後部署到 GitHub Pages。

## 家人怎麼看

1. 打開網站網址  
2. 輸入通行密碼（向行程負責人索取）  
3. 同一裝置約 14 天內會記住，不必重輸

## 自己改行程後怎麼更新

1. 編輯 `index.source.html`（明文原稿，勿直接改上線的 `index.html`）  
2. 確認本機有 `.site-password`（密碼檔，已加入 gitignore）  
3. 執行：

```bash
python scripts/lock_site.py
```

4. 提交並推送：

```bash
git add index.source.html index.html images
git commit -m "Update itinerary"
git push
```

## 注意

- GitHub Pages **沒有**伺服器端密碼功能；本站是把 HTML 內容 AES 加密後才公開。  
- 沒有密碼看不到行程內文；但無法防範「已知道密碼的人再轉傳」。  
- 倉庫請維持 **Private**，並只邀請需要一起改行程的家人當 collaborator。

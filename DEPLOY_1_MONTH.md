# 1 Aylik Canli Kullanim (Render)

Bu proje FastAPI + static HTML oldugu icin tek servis olarak Render'da calisabilir.

## Onkosullar

- GitHub hesabi + yeni bos repo (ornek: `sektor-rehberim`)
- Render hesabi (https://render.com)
- En az **Starter** plan (persistent disk icin; `render.yaml` icinde `plan: starter`)

---

## Bolum 1: GitHub'a Push (Cursor Terminal)

Proje klasorunde (`sektor_rehberim`) sirasiyla:

```bash
cd /Users/ahmet/Documents/sektor_rehberim

git init
git add .
git commit -m "Initial: Sektör Rehberim MVP + Render deploy"

git branch -M main
git remote add origin https://github.com/KULLANICI_ADIN/sektor-rehberim.git
git push -u origin main
```

**Notlar:**

- `KULLANICI_ADIN` ve repo URL'ini kendi GitHub'ina gore degistir.
- GitHub'da once **bos repo** olustur (README ekleme secenegini kapatabilirsin, cakisma olmasin).
- Ilk kez push ediyorsan GitHub kimlik dogrulamasi isteyebilir (PAT veya GitHub CLI).

---

## Bolum 2: Render'da Blueprint ile Deploy

1. https://render.com → giris yap / kayit ol.
2. Dashboard'da **New +** → **Blueprint**.
3. **Connect** ile GitHub hesabini bagla, repoyu sec.
4. Render `render.yaml` dosyasini otomatik bulur; **Apply** / **Create Blueprint** ile devam et.
5. Olusturulacak **Web Service** icin:
   - Build: `pip install -r backend/requirements.txt`
   - Start: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
   - Disk: `/var/data` (YAML'da tanimli)
6. **Deploy** bitene kadar bekle (ilk build 2-5 dk surebilir).

---

## Bolum 3: Canli Kontrol

Tarayicida (kendi Render URL'in):

- `https://<app-adin>.onrender.com/health` → `{"status":"ok"}`
- `https://<app-adin>.onrender.com/` → uygulama acilmali

Telefondan da ayni HTTPS adresi ile acabilirsin.

---

## Sorun Gider

### "Blueprint file render.yaml not found on main branch"

Bu, GitHub'daki **`main`** dalinda repo kokunde `render.yaml` **yok** demek (yerelde olmasi yetmez).

**Cozum:**

1. Bilgisayarda proje klasorunde kontrol et:
   ```bash
   ls -la render.yaml
   ```
2. Git durumuna bak:
   ```bash
   git status
   ```
3. Dosya "untracked" veya commitlenmemisse:
   ```bash
   git add render.yaml
   git commit -m "Add render.yaml for Render Blueprint"
   git push origin main
   ```
4. Dal adin `master` ise Render `main` arıyor olabilir:
   - Ya GitHub'da default branch'i `main` yap ve `main`'e push et,
   - Ya da `git branch -M main` ile dalı `main` yapip push et.

5. Render'da **dogru repoyu** sectiginden emin ol (baska bos repo bagli olmasin).

Sonra Render'da Blueprint'i tekrar dene.

| Sorun | Ne yap |
|-------|--------|
| Build hata | Render **Logs** sekmesinde `pip install` ciktisina bak |
| 502 / uyku | Free tier uyuyabilir; Starter + surekli calisma daha stabil |
| Veri sifirlandi | Disk mount ve `SQLITE_PATH=/var/data/app.db` ayarli mi kontrol et |

---

## Eski Kisa Ozet

1. GitHub'a push et.
2. Render'da **New + Blueprint** sec.
3. Reponu bagla, `render.yaml` otomatik okunur.
4. Deploy baslat.
5. `/health` ve `/` kontrol et.

## Neden Starter Plan?

- 1 aylik stabil kullanimda kalici veri gerekir.
- SQLite dosyasi `/var/data/app.db` altinda tutulur.
- Disk mount: `/var/data`

## Telefon Erisimi

- Render domaini HTTPS ile gelir (sertifika otomatik).
- Telefon tarayicisinda direkt acabilirsin.

## Notlar

- Bu setup MVP icin uygundur.
- Trafik buyurse Postgres/Firebase'e gecis onerilir.


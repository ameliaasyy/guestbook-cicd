# Buku Tamu Digital Kampus (Digital Guestbook)

Ujian Chunin - Cloud Computing, Telkom University
Cloud-Native Fullstack Application & Automated CI/CD Pipeline

## Anggota Kelompok
| Nama | NIM |
|------|-----|
| Putri Amelia | 101012330301 |
| Rivanda Abdillah | 101012330350 |
| Faiz Fajhri Kacaribu | 101012300318 |

## Studi Kasus
Nomor 1: Buku Tamu Digital Kampus. Sistem pencatat daftar tamu/pengunjung acara kampus.

## Arsitektur

```
Developer --git push--> GitHub --webhook--> Jenkins
                                              |
                  Checkout > Syntax Check > Build Image > Deploy > Health Check
                                              v
Browser --:8081--> [frontend: nginx] --app-net--> [backend: Python :5000]
                    bind mount ./frontend          named volume guestbook-db-data
                    /api/ -> backend:5000          -> /var/lib/backend_data/guestbook.json
```

- **backend**: Python REST API (`http.server`, tanpa framework), data disimpan ke `guestbook.json` di Named Volume `guestbook-db-data`.
- **frontend**: HTML + Vanilla JS (`fetch()`), disajikan Nginx dengan Bind Mount `./frontend`, sehingga perubahan UI langsung terlihat tanpa rebuild image.
- **network**: Custom Bridge Network `app-net`, frontend memanggil backend lewat service name `backend` (DNS Docker).
- **CI/CD**: Jenkins Declarative Pipeline (5 stage) dipicu GitHub Webhook setiap `git push` ke `main`.

## Struktur Repo
```
backend/app.py, backend/Dockerfile
frontend/index.html
nginx/default.conf
docker-compose.yml
Jenkinsfile
```

## API
| Method | Endpoint | Fungsi |
|--------|----------|--------|
| GET | /messages | Daftar tamu |
| POST | /messages | Tambah tamu (JSON: name, message) |
| DELETE | /messages?index=X | Hapus entri tamu |

Error handling: `400` (JSON/field tidak valid, index bukan angka), `404` (path atau index tidak ditemukan).

Contoh:
```bash
curl -X POST localhost:5001/messages -H "Content-Type: application/json" -d '{"name":"Budi","message":"Halo"}'
curl localhost:5001/messages
curl -X DELETE "localhost:5001/messages?index=0"
```

## Instalasi Lokal
Prasyarat: Docker dan Docker Compose.
```bash
git clone https://github.com/ameliaasyy/guestbook-cicd.git
cd guestbook-cicd
docker compose up -d --build
```
- UI: http://localhost:8081
- API: http://localhost:5001/messages

### Uji Data Immunity
```bash
docker rm -f guestbook-backend
docker compose up -d
curl localhost:5001/messages    # data masih ada
```

## Setup Jenkins
1. Install Docker, Java 21, dan Jenkins; tambahkan user `jenkins` ke grup `docker`.
2. Buat GitHub Personal Access Token (classic) dengan izin `repo` dan `admin:repo_hook`.
3. Buat job **Pipeline** bernama `guestbook-pipeline`: Definition *Pipeline script from SCM*, SCM *Git*, URL repo ini, branch `*/main`, Script Path `Jenkinsfile`.
4. Aktifkan **GitHub hook trigger for GITScm polling**.
5. Expose Jenkins ke internet dengan ngrok: `ngrok http 8080`.
6. GitHub repo > Settings > Webhooks > Add webhook: Payload URL `https://<domain-ngrok>/github-webhook/`, Content type `application/json`, event *push*.

## Pipeline (Jenkinsfile)
1. **Checkout**: ambil kode dari GitHub
2. **Syntax Check**: `python3 -m py_compile backend/app.py`
3. **Build Image**: `docker compose build`
4. **Automated Deployment**: `docker compose up -d --remove-orphans`
5. **Health Check**: `curl` ke `http://localhost:5001/messages`

## Video Demo
Link video: ISI_LINK_VIDEO

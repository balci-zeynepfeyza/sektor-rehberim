# Firestore Data Model (MVP Tasarımı)

Bu doküman, mevcut LocalSQLite MVP'nin veri şeklini Firestore'a taşımaya yönelik taslaktır.

## Koleksiyonlar (Collections)

### `companies/{companyId}`
Şirket sayfası için temel bilgiler.

- `name` (string, opsiyonel)
- `createdAt` (timestamp)
- `updatedAt` (timestamp)

> MVP’de ortalama puan hesabı için iki yol önerilir:
> 1) On-the-fly (komment sayısına göre query) -> düşük trafik MVP için yeterli
> 2) Cloud Function / scheduled job ile `companies/{id}.ratingSummary` alanını güncel tutmak -> daha ölçeklenebilir

### `comments/{commentId}`
Şirket yorumları ve 1-5 kategorik puanlar.

- `companyId` (string, required)
- `displayName` (string, required)  // anonim takma ad
- `message` (string, required)
- `ratings` (map, required)
  - `difficulty` (number 1..5)
  - `balance` (number 1..5)
  - `office` (number 1..5)
- `createdAt` (timestamp)

**Moderasyon için (MVP min):**

- Küfür filtresi server-side reddedilir; Firestore’a yazılmaz.

### `interviewQuestions/{questionId}`
Şirket için mülakat soruları havuzu.

- `companyId` (string, required)
- `category` (string enum: `technical | behavioral | general`)
- `question` (string, required)
- `createdAt` (timestamp)

### `reports/{reportId}`
Bir yorumun şikayet kaydı.

- `commentId` (string, required)
- `companyId` (string, required)
- `reason` (string, required)
- `status` (string: `open | closed | removed`)
- `createdAt` (timestamp)

## Opsiyonel alanlar (isterseniz)

### `companies/{companyId}.ratingSummary`
Kategori ortalamaları + genel ortalama + yorum sayısı.

- `ratingCount` (number)
- `avgDifficulty` (number)
- `avgBalance` (number)
- `avgOffice` (number)
- `avgOverall` (number)

## Güvenlik (Security) / Veri Gizliliği

- Yorumlarda/raporlarda `ip`, `email`, `userId` gibi kişisel bilgilerin hiç yazılmaması hedeflenir.
- Firestore tarafında kurallarla:
  - `comments/*` için `displayName`, `message`, `ratings`, `createdAt`, `companyId` dışındaki field’leri yazmaya izin verme (`allow write only for whitelisted fields`).
  - `reports/*` için de benzer şekilde sadece `commentId`, `companyId`, `reason`, `status`, `createdAt` yazılabilir olsun.

## Index Önerileri

- `comments`: `where companyId == ? order by createdAt desc`
- `interviewQuestions`: `where companyId == ? order by createdAt desc`
- `interviewQuestions` (kategori filtreli): `where companyId == ? and category == ? order by createdAt desc`


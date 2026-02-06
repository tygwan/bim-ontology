# BIM Ontology 배포 가이드

## 1. 직접 실행 (개발용)

```bash
cd bim-ontology
source venv/bin/activate
uvicorn src.api.server:app --host 0.0.0.0 --port 8001
```

**옵션**:
- `--reload`: 코드 변경 시 자동 재시작 (개발용)
- `--workers 4`: 다중 워커 (프로덕션용)
- `--host 0.0.0.0`: 외부 접속 허용

---

## 2. Docker 배포

### 빌드 및 실행

```bash
cd bim-ontology

# 기본 포트 (8000)
docker compose up --build -d

# 포트 변경
BIM_PORT=8002 docker compose up --build -d

# 로그 확인
docker compose logs -f

# 종료
docker compose down
```

### Docker 이미지 구성

- **Base**: python:3.12-slim
- **크기**: ~612MB
- **포트**: 8000 (내부)
- **볼륨**:
  - `./references:/app/references:ro` - IFC 파일 (읽기 전용)
  - `./data:/app/data` - RDF 캐시 (읽기/쓰기)

### 환경 변수

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `BIM_PORT` | 8000 | 호스트 포트 매핑 |
| `LOG_LEVEL` | info | 로깅 레벨 (debug/info/warning/error) |

---

## 3. 데이터 관리

### IFC 파일

`references/` 디렉토리에 IFC 파일을 배치합니다.

- IFC4 샘플 파일을 `references/` 디렉토리에 배치합니다.
- IFC2X3 파일도 지원됩니다.

### RDF 캐시

서버 첫 실행 시 IFC를 RDF로 변환하여 `data/rdf/`에 Turtle 파일로 저장합니다.
이후 재시작에서는 캐시 파일을 직접 로딩합니다.

```
data/rdf/<filename>.ttl    # IFC 변환 캐시 (Turtle 포맷)
```

캐시를 갱신하려면 해당 `.ttl` 파일을 삭제 후 서버를 재시작합니다.

---

## 4. 서버 설정

### IFC/RDF 경로 변경

`src/api/server.py`에서 기본 경로를 수정:

```python
DEFAULT_IFC_PATH = "references/<your-file>.ifc"
DEFAULT_RDF_PATH = "data/rdf/<your-file>.ttl"
```

### CORS 설정

기본값은 모든 오리진 허용 (`*`). 프로덕션에서는 제한 필요:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
```

---

## 5. 헬스 체크

```bash
curl http://localhost:8001/health
# {"status":"healthy","triples":39217}
```

Docker 환경에서 헬스 체크를 추가하려면 `docker-compose.yml`에:

```yaml
services:
  api:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

---

## 6. 포트 충돌 해결

```bash
# 포트 사용 중인 프로세스 확인
lsof -i :8001

# 해당 프로세스 종료
kill $(lsof -t -i :8001)
```

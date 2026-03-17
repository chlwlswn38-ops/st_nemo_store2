# Nemostore 대시보드 배포 가이드 (GitHub & Streamlit Cloud)

이 가이드는 로컬에서 개발된 대시보드를 온라인에 배포하는 과정을 안내합니다.

## 1. 필수 파일 확인
GitHub 리포지토리의 루트 또는 지정된 폴더에 다음 파일들이 포함되어야 합니다.

- `nemostore/src/dashboard.py`: 메인 소스 코드
- `nemostore/data/nemostore.db`: SQLite 데이터베이스 파일
- `nemostore/requirements.txt`: 라이브러리 목록

## 2. GitHub 업로드 과정

1. **GitHub 리포지토리 생성**: [GitHub](https://github.com)에서 새 리포지토리를 생성합니다.
2. **코드 푸시**:
   ```bash
   cd /Users/me/icb6/antigravity_project/fcicb6_proj2
   git init
   git add nemostore/
   git commit -m "Initial commit for Nemostore Dashboard"
   git branch -M main
   git remote add origin https://github.com/사용자계정/리포지토리이름.git
   git push -u origin main
   ```

## 3. Streamlit Cloud 배포 과정

1. **로그인**: [Streamlit Cloud](https://streamlit.io/cloud)에 접속하여 GitHub 계정으로 로그인합니다.
2. **App 생성**: 'Create app' 버튼을 클릭합니다.
3. **Repository 연결**:
   - **Repository**: 위에서 생성한 리포지토리를 선택합니다.
   - **Main file path**: `nemostore/src/dashboard.py`를 입력합니다.
4. **Deploy**: 'Deploy!' 버튼을 클릭하면 배포가 시작됩니다.

> [!IMPORTANT]
> 배포 시 `nemostore.db` 파일이 리포지거리에 포함되어 있어야 데이터를 정상적으로 불러올 수 있습니다.

## 4. 라이브러리 관리 (requirements.txt)
배포 환경에서는 다음 라이브러리들이 자동으로 설치됩니다.
- `streamlit`
- `pandas`
- `plotly`
- `numpy`

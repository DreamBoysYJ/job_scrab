# config 폴더

## 역할
스크래핑 설정 파일을 관리하는 폴더

## 파일 구조

### keywords.yaml
채용공고 검색에 사용할 키워드와 필터 설정

```yaml
keywords:        # 검색할 키워드 목록
location:        # 검색 지역 (예: "한국", "서울")
combination:     # 키워드 조합 방식 ("AND" 또는 "OR")
exclude:         # 제외할 키워드 목록
experience:      # 경력 필터 (min, max 년수)
```

## 사용 방법

### GitHub 웹에서 직접 수정
1. GitHub 저장소 접속
2. `config/keywords.yaml` 파일 클릭
3. 연필 아이콘 (Edit) 클릭
4. 키워드 수정 후 "Commit changes"

### 키워드 조합 방식
- **AND**: 모든 키워드가 포함된 공고만 검색
- **OR**: 키워드 중 하나라도 포함된 공고 검색

## 주의사항
- YAML 문법 준수 필요 (들여쓰기 등)
- 키워드는 반드시 리스트 형식으로 작성
- 특수문자가 포함된 키워드는 따옴표로 감싸기

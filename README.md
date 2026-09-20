# Presevka

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./assets/presevka-banner-dark.png">
    <source media="(prefers-color-scheme: light)" srcset="./assets/presevka-banner-light.png">
    <img alt="Presevka — 프리텐다드 × Iosevka" src="./assets/presevka-banner-light.png" width="100%">
  </picture>
</p>

<p align="center">
<span style="font-style: italic;">
  Iosevka에 Pretendard의 한글을 결합한 고정폭 글꼴<br>
</span>
</p>

---

> [!NOTE]
> Presevka는 [Iosevka](https://github.com/be5invis/Iosevka)를 코드와 라틴 문자의
기반으로, [Pretendard](https://github.com/orioncactus/pretendard)를 한글 글리프의
기반으로 삼는 독립적인 Modified Version입니다.
> Presevka는 Iosevka 또는 Pretendard의 공식 배포판이 아니며, 원 프로젝트와는 별개로 유지됩니다.

## 다운로드

[최신 버전 다운로드](https://github.com/kxxholee/presevka/releases/latest)

## 글꼴 구성

| 항목 | 값 |
| --- | --- |
| 라틴 advance | 500 units (1000 UPM) |
| 한글 advance | 1000 units (라틴 두 칸) |
| 현대 한글 음절 | 11,172자 (U+AC00–D7A3 전체) |
| 한글 호환 자모 | 53자 (U+3130–318F의 현대 자모 전체) |
| 페이스 | 9 weight × Upright/Italic = 18개 |

라틴은 Iosevka의 기본 500-unit 셀을 사용하고, 한글은 두 라틴 셀에 해당하는
1000-unit advance 안에 배치됩니다. Pretendard 한글 윤곽은 원본 비율을 유지한
채 가로로 2%만 확대하고, 나머지 폭은 좌우 여백으로 둡니다. Italic에서도 한글과
자모는 기울이지 않은 Pretendard 윤곽을 유지합니다.

> [!NOTE]
> 결합(조합용) 자모 U+1100–11FF와 Jamo Extended-A/B는 포함되지 않습니다.
> 한글 글리프의 기반인 Pretendard가 해당 글리프를 제공하지 않기 때문입니다.
> 한글이 NFD로 정규화된 텍스트(예: macOS 파일명)는 HarfBuzz 계열 렌더러가
> 자모를 완성형 음절로 다시 조합해 주므로 대부분의 터미널과 브라우저에서
> 정상적으로 표시되지만, 조합을 수행하지 않는 렌더러에서는 표시되지 않습니다.

## 소스에서 빌드

### 의존성

- Node.js 18 이상과 npm
- Python 3.11 이상
- [uv](https://docs.astral.sh/uv/)

### 빌드

```sh
git clone https://github.com/kxxholee/presevka.git
cd presevka

make doctor
make build
```

아홉 가지 weight의 Upright와 Italic, 총 18개 TTF가 `dist/`에 생성됩니다.
배포용 아카이브와 WOFF2가 필요하면 `make package`를 실행하면
`Presevka-<버전>-ttf.zip`과 `Presevka-<버전>-woff2.zip`이 만들어집니다.

<!-- 
Linux에서는 다음 명령으로 현재 사용자에게 바로 설치할 수 있습니다.

```sh
make install
```

설치 위치는 `${XDG_DATA_HOME:-$HOME/.local/share}/fonts/presevka`입니다. -->

## 라이선스

- 완성 폰트와 폰트 수정물: [SIL Open Font License 1.1](./LICENSE)
- Presevka의 Python/shell 빌더: [MIT](./LICENSE-CODE)
- 원본 저작권·Reserved Font Name: [OFL.txt](./OFL.txt)
- 원본 출처: [THIRD_PARTY.md](./THIRD_PARTY.md)
- 변경 이력: [FONTLOG.md](./FONTLOG.md)

## 크레딧

- [Iosevka](https://github.com/be5invis/Iosevka) — Renzhi Li / The Iosevka Project Authors
- [Pretendard](https://github.com/orioncactus/pretendard) — Kil Hyung-jin and upstream authors

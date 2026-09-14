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
Italic에서도 한글과 자모는 기울이지 않은 Pretendard 윤곽을 유지합니다.

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

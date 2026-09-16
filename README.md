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
라틴은 Iosevka의 기본 500-unit 셀을 사용하고, 한글은 두 라틴 셀에 해당하는
1000-unit advance 안에 배치됩니다. Pretendard 한글 윤곽은 원본 비율을 유지한
채 가로로 2%만 확대하고, 나머지 폭은 좌우 여백으로 둡니다.

### Iosevka 라틴 커스터마이징

Presevka의 기본 라틴 디자인은 Iosevka의 `ss14`(JetBrains Mono Style)
preset을 상속하고, 원본과 같은 500-unit 셀 폭을 사용합니다. 이 설정은
[`config/private-build-plans.toml`](./config/private-build-plans.toml)에 있습니다.

다른 Iosevka 스타일을 사용하려면 build plan에 원하는 stylistic set을
상속하도록 설정합니다. 예를 들어 Input Mono Style은 다음과 같습니다.

```toml
[buildPlans.PresevkaBase500.variants]
inherits = "ss18"
```

특정 글리프만 바꾸려면 같은 build plan에 variant override를 추가할 수 있습니다.

```toml
[buildPlans.PresevkaBase500.variants.design]
i = "serifed-asymmetric"
zero = "slashed"
```

사용 가능한 preset과 variant 이름은
[Iosevka v34.8.0 Custom Build 문서](https://github.com/be5invis/Iosevka/blob/v34.8.0/doc/custom-build.md)를
참고하세요. 설정을 바꾼 뒤 `make build`를 다시 실행하면 됩니다. Pretendard가
이미 준비된 작업 트리에서는 `./scripts/build_iosevka.sh`와
`./scripts/merge.sh`만 차례로 실행해도 됩니다.

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

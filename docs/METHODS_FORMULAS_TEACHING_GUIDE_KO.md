# PEC 방법론, 수식, 결과 해설 가이드

작성일: 2026-07-11  
대상 원고: `paper/icwsm_pec_gap_v47_author_year_protocol_blind_full.md`

이 문서는 PEC Gap 논문의 분석 방법론과 수식을 한글로 자세히 설명하기 위한 협업 검토용 문서입니다. 단순히 수식의 정의만 적는 것이 아니라, 각 수식이 왜 필요한지, 본 데이터에서는 어떤 의미로 해석되는지, 어떤 오해를 피해야 하는지까지 함께 설명합니다.

이 문서를 읽는 목표는 다음과 같습니다.

1. 논문의 핵심 개념인 Preference, Exposure, Surface, Consumption을 정확히 이해한다.
2. RQ1-RQ4에서 사용한 지표와 수식을 남에게 설명할 수 있다.
3. 본 데이터에서 나온 수치가 논문 주장을 어떻게 뒷받침하는지 이해한다.
4. 검토 과정에서 과장 없이 해석 범위를 설명할 수 있다.

## 1. 논문의 핵심 문제

개인화 뉴스 플랫폼은 보통 다음과 같은 선형 파이프라인처럼 이해됩니다.

1. 사용자가 선호를 입력한다.
2. 시스템이 그 선호를 바탕으로 뉴스를 추천한다.
3. 사용자가 추천된 뉴스를 클릭한다.
4. 플랫폼은 클릭을 사용자의 선호 또는 추천 성공으로 해석한다.

이 흐름은 직관적이지만 실제 모바일 뉴스 앱에서는 너무 단순합니다. 사용자는 추천 리스트만 보고 뉴스를 클릭하지 않습니다. 헤드라인 영역, 카테고리 탭, 홈/피드, 뉴스룸 탭, 검색, 알림, 기사 상세 페이지의 연관 기사 등 여러 surface를 통해 기사에 들어갑니다.

따라서 하나의 클릭은 여러 의미를 가질 수 있습니다.

- 진짜 선호일 수 있습니다.
- 눈에 띄는 헤드라인 때문일 수 있습니다.
- 속보라서 클릭했을 수 있습니다.
- 앱의 UI 경로상 자연스럽게 보였기 때문일 수 있습니다.
- 습관적으로 특정 탭을 보다가 클릭했을 수 있습니다.
- 추천 리스트와 전혀 상관없는 다른 surface에서 발생했을 수 있습니다.

이 논문의 핵심은 바로 이것입니다.

> 사용자의 명시적 선호, 시스템이 기록한 추천 노출, 앱 surface를 통한 클릭 경로, 실제 클릭 소비는 서로 관련은 있지만 서로 대체할 수 없다.

이 문장을 영어 논문에서는 다음처럼 표현합니다.

> Preferences, logged exposure, and clicks are all meaningful signals, but none can safely stand in for the others.

이 문장이 논문의 중심입니다. 모든 수식과 분석은 이 문장을 증명하거나 정교하게 제한하기 위해 존재합니다.

## 2. PEC 프레임워크

PEC는 Preference-Exposure-Consumption의 약자입니다. 여기에 실제 모바일 앱에서는 사용자가 어떤 화면 경로에서 기사를 만났는지가 중요하기 때문에 surface pathways, 즉 S layer를 함께 둡니다. 여기서 S는 인과적 mediation 분석을 뜻하지 않습니다. 앱 안의 headline, category, home/feed, newsroom, article detail, search, notification 같은 관측 가능한 진입 경로를 뜻합니다.

중요한 점은 PEC gap이 하나의 종합 점수가 아니라는 것입니다. PEC gap은 preference-consumption alignment, exposure-consumption traceability, exposure-consumption diversity shift, structured divergence처럼 관계별로 정의되는 여러 mismatch의 묶음입니다. 그래서 각 분석은 어떤 layer 관계를 비교하는지, 분모가 무엇인지, 어떤 보정이나 baseline을 쓰는지, 그리고 로그가 어디까지 해석을 허용하는지를 함께 밝혀야 합니다.

### 2.1 Preference, P

Preference는 사용자가 명시적으로 말하거나 설정한 선호입니다. 본 데이터에서는 두 가지 형태가 있습니다.

첫째, 사용자가 선택한 카테고리와 선호 매체/source입니다. 이것은 set 형태로 볼 수 있습니다. 예를 들어 사용자가 정치, 경제, IT를 선택했다면 stated category preference set이 `{정치, 경제, IT}`가 됩니다.

둘째, weighted profile-state입니다. 이것은 사용자의 프로필 안에 저장된 카테고리별 또는 source별 확률/가중치 형태의 값입니다. 예를 들어 정치 0.35, 경제 0.20, 국제 0.15처럼 분포로 볼 수 있습니다. 이 값은 가입 또는 온보딩 시점의 정보뿐 아니라 사용자가 앱 사용 중 preference panel에서 업데이트할 수 있는 현재 프로필 snapshot입니다.

중요한 제한점은, 본 연구가 완전한 preference edit history를 갖고 있지는 않다는 것입니다. 즉, 언제 어떤 선호를 수정했는지의 시간순 기록은 없습니다. 그래서 논문은 이것을 “current observed profile-state snapshot”으로 조심스럽게 부릅니다.

### 2.2 Exposure, E

Exposure는 시스템이 추천 리스트에 기록한 기사입니다. 본 원고에서 말하는 exposure는 전체 노출이 아니라 `logged recommendation exposure`입니다.

이 차이가 매우 중요합니다. 사용자는 앱에서 여러 방식으로 기사를 볼 수 있지만, 본 연구가 가진 추천 로그는 특정 user-date recommendation list입니다. 따라서 RQ2에서 “클릭이 추천에 의해 발생했는가?”를 묻는 것이 아니라, “클릭된 기사가 그날 그 사용자에게 기록된 추천 리스트에 있었는가?”를 묻습니다.

그래서 same-day hit는 CTR이 아닙니다. CTR은 추천 노출을 분모로 놓고 그중 몇 개가 클릭됐는지 보는 지표입니다. 본 연구는 반대로 클릭을 기준으로, 그 클릭이 logged recommendation exposure에 traceable한지 봅니다.

### 2.3 Surface, S

Surface는 사용자가 어떤 앱 경로에서 기사를 클릭했는지를 의미합니다. 해당 앱에서는 headline, category, home/feed, newsroom, article-detail, search, notification 같은 경로가 있습니다.

Surface가 중요한 이유는 추천 리스트가 전체 앱 경험을 대표하지 않기 때문입니다. 사용자가 headline 영역에서 많이 클릭한다면, 추천 리스트가 다양하더라도 클릭 소비는 headline surface의 영향을 크게 받을 수 있습니다.

이 논문에서 newsroom은 외부 사이트에서 들어온 링크가 아닙니다. 앱 내부에 있는 newsroom 탭 또는 newsroom 관련 surface를 의미합니다.

### 2.4 Consumption, C

Consumption은 사용자가 실제로 클릭한 기사입니다. 논문에서는 click consumption이라고 부릅니다. 다만 이것도 complete attention은 아닙니다.

클릭은 기사를 열었다는 뜻이지, 끝까지 읽었다는 뜻은 아닙니다. dwell time, scroll depth, reading completion이 없기 때문에 논문은 “attention”이라는 단어를 조심스럽게 씁니다. 제목에는 “Exposure Is Not Attention”이 들어가지만, 본문에서는 observed click consumption으로 제한합니다.

## 3. 데이터 객체와 표기법

사용자 \(u\)에 대해 다음 기호를 씁니다.

- \(P_{cat}(u)\): 사용자의 stated category preference set.
- \(P_{pub}(u)\): 사용자의 stated publisher/source preference set.
- \(E(u,d)\): 사용자 \(u\)가 날짜 \(d\)에 logged recommendation exposure로 받은 기사 집합.
- \(E_u=\bigcup_d E(u,d)\): 전체 관측 기간 동안 사용자 \(u\)에게 기록된 모든 추천 노출 기사.
- \(C_u\): 사용자 \(u\)가 클릭한 기사 집합.
- \(C^{top}_{cat}(u)\): 사용자 \(u\)가 가장 많이 클릭한 상위 3개 카테고리. 클릭 카테고리가 3개보다 적으면 가능한 만큼만 사용합니다.
- \(p^P_u\): weighted profile-state distribution.
- \(p^E_u\): logged exposure distribution.
- \(p^C_u\): click consumption distribution.

각 기사 \(i\)는 다음 metadata를 갖습니다.

- \(\operatorname{cat}(i)\): 기사 카테고리
- \(\operatorname{pub}(i)\): 매체 또는 publisher
- \(\operatorname{date}(i)\): 발행일 또는 분석에 쓰인 날짜

핵심은 raw log를 바로 비교하지 않고, category/publisher distribution으로 바꿔서 비교한다는 것입니다. 그래야 preference, exposure, consumption을 같은 좌표계에서 비교할 수 있습니다.

## 4. RQ1: Preference-Consumption Alignment

RQ1은 다음 질문입니다.

> 사용자가 명시한 선호는 실제 클릭 소비와 얼마나 맞는가?

이 질문은 단순해 보이지만 중요합니다. 많은 추천 시스템은 사용자가 설정한 선호가 실제 소비를 잘 대표한다고 가정합니다. 본 원고는 이 가정이 어느 정도 성립하고 어느 지점에서 깨지는지 측정합니다.

### 4.1 Top-Category Match

가장 직관적인 지표는 top-category match입니다. 사용자가 가장 많이 클릭한 카테고리가 사용자의 stated category preference 안에 들어 있는지 확인합니다.

예를 들어 사용자가 선호 카테고리로 정치, 경제, IT를 선택했고, 실제로 가장 많이 클릭한 카테고리가 정치라면 match입니다. 반대로 가장 많이 클릭한 카테고리가 스포츠인데 선호 목록에 스포츠가 없다면 mismatch입니다.

본 결과는 profile과 click이 있는 698명을 분모로 한 77.22%입니다. Stated-category set이 비어 있는 19명도 이 분모에는 nonmatch로 포함됩니다.

이 수치는 꽤 긍정적입니다. 사용자가 설정한 선호가 완전히 무의미하지 않다는 뜻입니다. 대부분의 사용자에게서 가장 강한 클릭 카테고리는 stated preference 안에 들어 있습니다.

하지만 이것만으로 “선호가 실제 소비를 잘 설명한다”고 해석하면 범위를 벗어납니다. 왜냐하면 top-category match는 가장 큰 카테고리 하나가 들어 있는지만 보기 때문입니다. 사용자의 전체 소비 폭이 선호와 맞는지는 알 수 없습니다.

그래서 Jaccard가 필요합니다.

이 지표의 장점은 해석이 매우 직접적이라는 점입니다. 사용자에게 “가장 많이 소비한 주제가 애초에 선호로 설정되어 있었는가?”라는 질문에 답합니다. 반대로 한계도 명확합니다. 사용자가 정치 기사를 60%, 경제 기사를 20%, 스포츠 기사를 20% 클릭했더라도 top category만 보면 정치 하나만 남습니다. 즉, top-category match는 dominant orientation, 즉 가장 강한 관심 방향을 보는 지표이지 consumption breadth를 보는 지표가 아닙니다.

본 데이터에서 77.22%라는 값은 stated preference가 완전히 형식적인 입력값은 아니라는 근거가 됩니다. 그러나 이 값이 높다고 해서 preference layer가 consumption layer를 대체할 수 있다는 뜻은 아닙니다. 바로 이 긴장이 RQ1의 핵심입니다. 선호는 의미가 있지만 얕고, 클릭 소비의 폭과 맥락까지 모두 설명하지는 못합니다.

### 4.2 Category Jaccard Overlap

Jaccard overlap은 두 집합의 공통 부분을 두 집합이 함께 포괄하는 전체 범위와 비교하는 set-similarity metric입니다. 단순히 “몇 개가 겹쳤는가”만 보는 것이 아니라, 겹친 항목 수를 두 집합 중 어느 쪽에라도 등장한 항목 전체의 크기로 나눕니다. 그래서 Jaccard는 “공통 관심사가 있다”는 사실과 “그 공통 관심사가 전체 관심/소비 폭에서 얼마나 큰 비중을 차지하는가”를 동시에 반영합니다.

\[
J_u=\frac{|P_{cat}(u)\cap C^{top}_{cat}(u)|}{|P_{cat}(u)\cup C^{top}_{cat}(u)|}
\]

분자는 두 집합의 교집합입니다. 즉, 사용자가 선호한다고 말한 카테고리와 실제로 많이 클릭한 카테고리 중 겹치는 항목 수입니다.

분모는 두 집합의 합집합입니다. 즉, 두 집합 중 어느 쪽에라도 등장한 전체 카테고리 수입니다.

Jaccard는 0에서 1 사이입니다.

- 0이면 전혀 겹치지 않습니다.
- 1이면 완전히 같습니다.
- 0.2라면 전체적으로는 꽤 약한 overlap입니다.

예를 들어 stated preference가 \(\{\text{Politics}, \text{Economy}, \text{Tech}\}\)이고 top clicked categories가 \(\{\text{Politics}, \text{Sports}, \text{Culture}\}\)라면, 교집합은 Politics 하나이고 합집합은 Politics, Economy, Tech, Sports, Culture 다섯 개입니다. 따라서 \(J=1/5=0.2\)입니다. 이 사용자는 top-category match 관점에서는 Politics가 잡혔으므로 “주된 방향은 어느 정도 맞았다”고 볼 수 있지만, Jaccard 관점에서는 전체 소비 폭의 overlap이 낮습니다.

중요한 edge case도 있습니다. 만약 stated category set이 비어 있고 클릭 category set은 비어 있지 않다면 Jaccard는 정의 불가능한 것이 아니라 0입니다. 예를 들어 \(P=\varnothing\), \(C=\{\text{Politics},\text{Sports},\text{Economy}\}\)이면 교집합은 \(\varnothing\)이고 합집합은 \(C\)입니다. 따라서

\[
J=\frac{|\varnothing|}{|C|}=0.
\]

분자와 분모가 같아져서 1이 되는 것이 아닙니다. 1이 되려면 두 집합이 완전히 같아야 하는데, empty preference set과 nonempty click set은 완전히 다른 집합입니다. 최종 원고가 19명의 empty stated-category users를 \(J_u=0\)으로 포함하는 이유가 바로 이것입니다.

Jaccard가 중요한 이유는 “맞은 항목 수”만 보지 않고 “전체 가능한 항목 수 대비 얼마나 겹쳤는가”를 보기 때문입니다. 예를 들어 선호와 클릭이 하나만 겹쳐도, 두 집합이 각각 매우 작으면 Jaccard가 높을 수 있고, 두 집합의 폭이 넓으면 Jaccard는 낮아질 수 있습니다. 따라서 Jaccard는 단순한 hit 여부보다 breadth mismatch에 민감합니다.

본 원고에서 \(C^{top}_{cat}(u)\)를 상위 3개 클릭 카테고리로 정의한 이유도 여기에 있습니다. 클릭된 모든 카테고리를 쓰면 드문 클릭이나 우연한 클릭까지 과도하게 반영될 수 있고, top-1만 쓰면 소비의 폭을 거의 보지 못합니다. top-3는 dominant consumption을 보되, 단일 카테고리보다 넓은 소비 구조를 포착하기 위한 절충입니다. 클릭 카테고리가 3개보다 적은 사용자는 관측된 만큼만 사용합니다.

698명 전체에서 primary 평균은 0.2283, 중앙값은 0.2000입니다. 현재 스냅샷에 explicit stated-category set이 빈 19명은 클릭 집합과의 overlap을 0으로 포함합니다. Nonempty stated set 679명만 보는 sensitivity 평균은 0.2347이고 중앙값은 동일합니다. 여기서 nonempty-set sensitivity란 “empty stated-category 19명을 빼고, 적어도 하나의 stated category가 있는 사용자들만 대상으로 같은 Jaccard 평균을 다시 계산한 값”입니다. 즉 primary result는 전체 698명을 대표하고, sensitivity result는 “명시적으로 category preference를 표현한 사용자들 사이에서도 결론이 비슷한가”를 확인합니다.

같은 규칙을 click-history sensitivity에도 적용하면 top-3 Jaccard 평균은 click 5회 이상 사용자에서 0.3004(n=302), 10회 이상 사용자에서 0.3104(n=175)입니다. 전체 cohort보다 높지만 완전한 overlap과는 여전히 거리가 있습니다.

Observed result는 10,000회 permutation으로 만든 두 chance check보다 높습니다. Shuffled-set null은 top-category match 61.54%와 mean Jaccard 0.161, size-preserving category-frequency null은 54.81%와 0.137입니다.

이 결과가 중요한 이유는 top-category match와 다른 이야기를 하기 때문입니다.

Top-category match 77.22%는 “가장 중요한 클릭 카테고리는 선호 안에 들어 있는 경우가 많다”는 뜻입니다. 반면 primary Jaccard 0.2283은 “전체 소비 폭은 선호 세트와 많이 다르다”는 뜻입니다.

따라서 RQ1의 정확한 결론은 다음입니다.

> Stated preferences are meaningful but shallow.

한글로는 이렇게 설명할 수 있습니다.

> 명시적 선호는 사용자의 주된 관심 방향은 잡지만, 실제 소비의 전체 폭과 상황적 변동까지 충분히 설명하지는 못한다.

### 4.3 Divergence Score

논문에서는 Jaccard를 바탕으로 divergence를 정의합니다.

\[
D_u = 1 - J_u
\]

Jaccard가 alignment라면 divergence는 mismatch입니다. Jaccard가 높으면 divergence는 낮고, Jaccard가 낮으면 divergence는 높습니다.

이 값은 RQ4 모델링에서 high-divergence user를 정의할 때 사용됩니다. 하지만 이 점을 조심해야 합니다.

Divergence가 높다는 것은 사용자가 이상하다거나, 시스템이 실패했다는 뜻이 아닙니다. 사용자가 선호를 오래 업데이트하지 않았을 수도 있고, 특정 시기에 속보를 많이 클릭했을 수도 있고, headline surface에서 우연히 눈에 띈 기사를 클릭했을 수도 있습니다. 따라서 divergence는 “문제 사용자” 라벨이 아니라 “preference-consumption mismatch가 큰 사용자”라는 audit label입니다.

수식 자체는 단순하지만, 해석상 역할은 큽니다. \(D_u=1-J_u\)는 RQ1의 descriptive metric을 RQ4의 diagnostic label로 연결합니다. 즉, “선호와 소비가 얼마나 안 맞는가”를 사용자 단위로 수치화한 뒤, 이 값이 관측 가능한 프로필 상태나 행동 특성과 구조적으로 관련되는지 확인합니다. 이 연결 덕분에 논문은 단순 평균 비교에서 끝나지 않고, mismatch가 어떤 사용자 조건에서 더 뚜렷한지까지 살펴볼 수 있습니다.

다만 label이 preference-consumption 관계에서 정의되기 때문에 RQ4 모델은 production prediction이 아니라 bounded diagnostic입니다. 모델이 높은 AUC를 얻더라도, 그것은 “향후 사용자를 타깃팅할 수 있다”는 주장이 아니라 “mismatch가 완전한 노이즈는 아니며 관측 가능한 흔적과 관련된다”는 주장으로 제한됩니다.

### 4.4 Weighted Preference-Click Cosine

Set-based preference는 단순합니다. 선택했는지 안 했는지만 봅니다. 하지만 weighted profile-state는 카테고리별 가중치가 있으므로 vector로 볼 수 있습니다.

Cosine similarity는 두 벡터가 같은 방향을 향하는지 보는 vector-similarity metric입니다. 여기서 “방향”이란 각 category에 놓인 상대적 비중의 패턴을 뜻합니다. 두 벡터의 길이, 즉 전체 규모가 달라도 비중이 증가하고 감소하는 패턴이 같으면 cosine은 높게 나옵니다.

\[
\cos(p^P_u,p^C_u)=
\frac{p^P_u\cdot p^C_u}{\|p^P_u\|\|p^C_u\|}
\]

여기서 \(p^P_u\)는 profile-state distribution이고 \(p^C_u\)는 click distribution입니다.

계산할 때는 클릭된 category만 놓고 계산하는 것이 아니라, 두 벡터가 놓이는 공통 category 좌표계를 먼저 만듭니다. 실무적으로는 preference에 등장한 category와 click에 등장한 category의 union 또는 전체 taxonomy를 기준으로 좌표를 만들고, 한쪽에 없는 category는 0으로 채웁니다. 예를 들어 preference는 5개 category에 weight가 있고 실제 클릭은 그중 3개 category에서만 발생했다면, 3개만 잘라서 계산하는 것이 아닙니다. 클릭하지 않은 preference category도 click vector에서는 0으로 들어가야 합니다. 그래야 “선호에는 있었지만 클릭에는 없었던 방향”이 similarity를 낮추는 정보로 반영됩니다.

왜 방향만 본다고 하는지 숫자로 보면 쉽습니다. 벡터 \(a=(1,2)\)와 \(b=(2,4)\)를 생각해 봅시다. \(b\)는 \(a\)를 정확히 2배 키운 벡터입니다. 두 벡터의 dot product는 \(1\cdot 2+2\cdot4=10\)입니다. 각 벡터의 길이는 \(\|a\|=\sqrt{1^2+2^2}=\sqrt5\), \(\|b\|=\sqrt{2^2+4^2}=\sqrt{20}=2\sqrt5\)입니다. 따라서

\[
\cos(a,b)=\frac{10}{\sqrt5\cdot 2\sqrt5}=\frac{10}{10}=1.
\]

크기는 다르지만 한 벡터가 다른 벡터의 양의 배수이므로 방향은 완전히 같습니다. 그래서 cosine은 1입니다. 반대로 두 벡터가 서로 다른 category에 weight를 둔다면 dot product가 작아지고 cosine도 낮아집니다.

Cosine이 높다는 것은 profile에서 높은 weight를 받은 카테고리와 click에서 높은 share를 가진 카테고리가 비슷하다는 뜻입니다.

본 결과에서 category preference-click cosine은 0.452입니다. 이것은 set-based Jaccard보다 더 강한 directional signal이 있다는 뜻입니다. 즉, 단순히 “선택했는지”보다 “어느 category에 상대적으로 더 많은 profile weight가 놓였는지”가 더 많은 정보를 담고 있습니다.

하지만 0.452는 완전한 정렬도 아닙니다. weighted profile-state는 실제 클릭 소비를 어느 정도 설명하지만, 완전히 대체하지는 못합니다.

Cosine similarity를 쓰는 이유는 두 분포의 “크기”보다 “방향”을 보기 위해서입니다. 어떤 사용자가 전체적으로 클릭 수가 많거나 적더라도, 카테고리별 비중의 방향이 profile-state와 비슷하면 cosine이 높아집니다. 따라서 cosine은 사용자 활동량의 절대 규모보다 preference vector와 click vector의 구조적 유사성을 보는 데 적합합니다.

학문적으로 이 지표는 set overlap과 distributional alignment 사이의 중간 위치에 있습니다. Jaccard는 선택 여부만 보고, JS divergence는 전체 확률분포의 차이를 봅니다. Cosine은 “어떤 카테고리에 상대적으로 더 큰 weight가 놓였는가”를 비교합니다. 본 데이터에서 0.452라는 값은 weighted profile-state가 단순 preference count보다 더 많은 정보를 담고 있음을 보여주지만, 동시에 절반 수준의 alignment에 그친다는 점에서 profile-state를 click consumption의 대체물로 쓰면 안 된다는 결론도 뒷받침합니다.

우리 결과를 쉬운 말로 풀면 다음과 같습니다.

- mean profile weight on top clicked category 0.143: 사용자가 가장 많이 클릭한 category가 profile-state에서 평균 14.3% 정도의 weight를 받았다는 뜻입니다. 완전히 무시된 것은 아니지만, profile의 중심을 압도적으로 차지한 것도 아닙니다.
- mean preference mass on top three clicked categories 0.264: 실제로 많이 클릭한 상위 category 세 개에 profile weight의 평균 26.4%가 놓였다는 뜻입니다. 클릭 소비의 주된 영역 일부는 profile에 반영되어 있지만, 나머지 profile mass는 다른 category에도 많이 퍼져 있습니다.
- mean category preference-click cosine 0.452: category 수준에서는 preference vector와 click vector가 어느 정도 같은 방향을 갖습니다. 무작위/no-signal처럼 0에 가깝지는 않지만, 1에 가까운 강한 정렬도 아닙니다.
- mean publisher preference-click cosine 0.080: publisher/source 수준에서는 방향성이 매우 약합니다. 사용자가 클릭한 publisher와 profile-source weight의 방향이 거의 맞지 않는다는 뜻입니다.

### 4.5 Publisher/Source Alignment

같은 분석을 publisher/source 수준에서도 합니다.

본 결과는 다음과 같습니다.

- top clicked publisher에 할당된 평균 profile weight: 0.014
- publisher preference-click cosine: 0.080

이는 매우 약한 정렬입니다. 다만 category와 publisher/source 수치를 같은 눈금에서 직접 비교하면 안 됩니다. 카테고리는 가능한 값의 수가 비교적 작고 고정된 반면, publisher/source는 가능한 값이 훨씬 많아 profile weight가 더 넓게 분산될 수 있습니다. 따라서 0.014를 “category weight보다 단순히 몇 배 낮다”는 식으로 해석하기보다는, high-cardinality source space에서 사용자의 top clicked publisher가 profile-state 안에서 거의 salient하게 잡히지 않았다는 보수적 신호로 읽는 것이 더 정확합니다.

즉, 여기서 안전한 결론은 “source preference가 category preference보다 절대적으로 나쁘다”가 아니라, 본 데이터의 현재 profile representation에서는 category-level preference가 broad topical orientation을 더 잘 포착하고, source-level preference는 실제 publisher-level click consumption을 설명하는 신호가 훨씬 희박하다는 것입니다.

이 결과는 논문에 중요한 nuance를 줍니다. Preference도 하나가 아닙니다. category preference와 publisher preference의 설명력은 다릅니다.

## 5. RQ2: Exposure-Consumption Traceability

RQ2는 다음 질문입니다.

> 실제 클릭 소비 중 얼마나 많은 것이 logged recommendation exposure로 trace 가능한가?

여기서 traceability라는 단어가 중요합니다. 원인(cause)을 말하는 것이 아닙니다. 사용자가 어떤 기사를 클릭했을 때, 그 기사가 같은 날 그 사용자에게 기록된 추천 리스트에 있었는지를 확인하는 것입니다.

### 5.1 Same-Day Hit

수식은 다음과 같습니다.

\[
H_{ui}=\mathbf{1}\{i\in E(u,\operatorname{date}(i))\}
\]

이 값은 indicator입니다.

- 클릭한 기사 \(i\)가 같은 날짜의 추천 리스트 \(E(u,d)\) 안에 있으면 1
- 없으면 0

본 결과는 다음과 같습니다.

- matched clicks: 17,232
- same-day recommendation lists가 있는 comparable clicks: 11,440
- same-day hits: 1,292
- same-day hit rate: \(1{,}292/11{,}440=11.29\%\)
- six-month recommendation-history overlaps: 2,477
- six-month recommendation-history overlap rate: \(2{,}477/17{,}232=14.37\%\)

이 수치를 해석할 때 가장 조심해야 할 점은, same-day hit는 CTR이 아니라는 것입니다. CTR은 추천된 기사 중 클릭된 비율입니다. Same-day hit는 클릭된 기사 중 추천 리스트에서 찾을 수 있는 비율입니다.

따라서 11.29%를 보고 “추천 성능이 낮다”고 해석하면 범위를 벗어납니다. 이 수치는 logged recommendation layer가 click consumption의 일부를 trace할 수 있지만 전체를 설명하지는 못한다는 뜻입니다.

분모가 무엇인지가 핵심입니다. CTR은 보통 exposure를 분모로 둡니다. 즉, “보여준 것 중 얼마나 클릭됐는가”를 봅니다. 반면 same-day hit는 click을 분모로 둡니다. 즉, “클릭된 것 중 얼마나 추천 로그에서 찾을 수 있는가”를 봅니다. 그래서 본 원고의 same-day hit는 recommender performance metric이 아니라 traceability metric입니다.

여기서도 두 hit rate의 분모가 다릅니다. Same-day hit는 “클릭 날짜에 그 사용자에게 same-day recommendation list가 실제로 존재하는 경우”만 비교할 수 있습니다. 그래서 분모가 전체 matched clicks 17,232가 아니라 comparable clicks 11,440입니다. 그중 1,292개 클릭 기사만 같은 날짜 추천 리스트 안에서 발견되므로 \(1{,}292/11{,}440=11.29\%\)가 됩니다.

반면 six-month recommendation-history overlap은 날짜를 엄격히 같은 날로 제한하지 않습니다. 해당 사용자의 전체 logged recommendation history 어딘가에 그 클릭 기사가 있었는지를 봅니다. 그래서 분모는 전체 matched clicks 17,232이고, 그중 2,477개가 추천 이력 안에서 발견되어 \(2{,}477/17{,}232=14.37\%\)가 됩니다. 이 통계는 click-date ordering을 완화하므로 broad overlap diagnostic으로만 해석합니다.

본 데이터에서 same-day hit 11.29%는 작아 보일 수 있지만, 모바일 뉴스 앱의 multi-surface 구조를 고려하면 이 숫자는 logged recommendation exposure가 클릭 소비의 일부 경로만 포착한다는 사실을 보여줍니다. 이 수치가 date-matched logged-list candidate-pool baseline보다 높다는 점은 추천 로그가 신호를 갖는다는 뜻이고, 동시에 전체 클릭의 다수가 추천 로그 밖에서 발생한다는 점은 logged exposure가 total exposure가 아님을 보여줍니다.

### 5.2 Date-Matched Random Baseline

Hit rate는 baseline 없이 해석하면 위험합니다. 그래서 날짜를 맞춘 logged-list candidate-pool baseline을 둡니다.

질문은 이렇습니다.

> 같은 날짜의 후보 기사 풀에서 추천 리스트와 같은 크기의 random list를 뽑았다면, 클릭된 기사가 우연히 포함될 확률은 얼마인가?

본 결과는 다음과 같습니다.

- logged same-day hit: 11.29%
- date-matched random hit: 9.13%

추천 로그가 random보다 높습니다. 즉, logged recommendation exposure는 완전히 무의미한 노이즈가 아닙니다. 그러나 차이가 매우 크지는 않습니다. 그래서 논문은 추천이 “signal-bearing yet partial”하다고 말합니다.

이 표현이 중요합니다.

> Signal-bearing: random보다 높으므로 신호가 있다.
> Partial: 전체 클릭 소비를 다 설명하지는 못한다.

날짜를 맞추는 이유는 뉴스 소비가 강한 시간성을 갖기 때문입니다. 특정 날짜에는 특정 속보, 정치 이벤트, 스포츠 경기, 경제 뉴스가 전체 사용자에게 동시에 중요해질 수 있습니다. 날짜를 맞추지 않은 baseline은 이런 news cycle 효과를 통제하지 못합니다. Date-matched logged-list candidate-pool baseline은 적어도 같은 날짜의 로그된 추천 후보 풀 안에서 우연 포함 가능성을 비교하게 해줍니다. 이 풀은 전체 production serving eligibility를 복원한 것이 아니라 그날 로그된 추천 목록들의 union이라는 한계가 있습니다.

따라서 11.29% 대 9.13%의 차이는 “개인화 추천이 클릭과 아무 관련이 없다”는 해석을 반박하지만, “개인화 추천이 클릭을 강하게 유발했다”는 주장까지 허용하지는 않습니다. 이 차이는 추천 로그가 날짜별 기사 풀의 단순 우연보다 더 많은 traceability signal을 담고 있음을 보여주는 제한적 근거입니다.

### 5.3 Top-k Lift

Top-k lift는 추천 리스트 상위 k개가 random보다 얼마나 더 잘 clicked item을 포함하는지 봅니다.

\[
Lift_k=\frac{\mathbb{E}[H^k_{obs}]}{\mathbb{E}[H^k_{rand}]}
\]

본 결과는 다음과 같습니다.

- top-5 logged hit: 4.99%
- top-5 random hit: 3.41%
- top-5 lift: 1.47x

1.47x는 상위 5개 추천이 random보다 약 47% 더 자주 클릭된 기사를 포함한다는 뜻입니다.

이 수치는 logged recommendation layer가 무의미하지 않다는 근거입니다. 하지만 이것도 인과효과는 아닙니다. 사용자가 추천을 보고 클릭했는지, 다른 surface에서 봤는지, 이미 관심 있던 기사였는지는 알 수 없습니다. 따라서 traceability signal로 해석합니다.

Lift는 절대 hit rate가 작을 때 특히 유용합니다. 예를 들어 top-5 hit가 4.99%라고 하면 숫자 자체는 작아 보입니다. 하지만 같은 조건에서 random top-5가 3.41%라면, 추천 상위권에는 clicked item이 random보다 더 자주 들어간 것입니다. 그래서 lift는 “절대적으로 얼마나 많이 맞혔는가”보다 “동일한 기회 구조에서 random보다 얼마나 더 나은가”를 보여줍니다.

다만 top-k lift도 ranking quality 전체를 평가하는 지표는 아닙니다. 우리는 clicked item이 추천 리스트 상위 k개에 있었는지만 확인할 뿐, 사용자가 실제로 그 위치를 봤는지, 다른 화면에서 같은 기사를 봤는지, 추천 순위가 클릭을 일으켰는지는 알 수 없습니다. 따라서 top-k lift는 E-C traceability의 상대적 강도를 보여주는 보조 지표입니다.

### 5.4 Popularity-Aware Baseline

Random baseline은 우연성은 통제하지만 popularity는 충분히 통제하지 못합니다. 어떤 기사는 그날 매우 인기 있어서 많은 추천 리스트에 들어가고 많은 사용자가 클릭할 수 있습니다.

그래서 popularity-aware baseline을 둡니다.

- 같은 날 다른 사용자 추천 리스트에서 많이 등장한 기사
- 전날 많이 클릭된 기사
- 전주에 많이 클릭된 기사

본 원고는 logged recommendation hit가 이런 단순 popularity baseline보다도 높다고 보고합니다. 하지만 이 역시 강한 personalization causal effect가 아니라, candidate-pool과 generic popularity baseline을 넘어서는 제한된 traceability signal입니다.

## 6. Surface Pathways

Surface-pathway analysis는 사용자가 어떤 앱 경로에서 기사를 클릭했는지를 분석합니다.

본 결과에서 주요 surface share는 다음과 같습니다.

- headline: 65.4%
- category: 14.0%
- home/feed: 9.3%
- newsroom: 7.0%
- article-detail: 4.1%

이 결과는 매우 중요합니다. 클릭의 상당 부분이 headline surface에서 발생합니다. 이는 추천 리스트만으로 click consumption을 설명할 수 없다는 것을 보여줍니다.

또한 surface별 same-day hit rate가 다릅니다. Category click은 headline click보다 same-day recommendation hit가 높습니다. 즉, surface마다 logged recommendation exposure와 연결되는 정도가 다릅니다.

여기서 핵심 문장은 다음입니다.

> Surface pathways are not merely entry points; they condition how profile state, logged exposure, and click consumption align.

한글로는 이렇게 설명할 수 있습니다.

> 앱의 surface는 단순한 클릭 경로가 아니라, 사용자의 선호, 추천 노출, 실제 소비가 서로 어떻게 연결되는지를 조건짓는 구조다.

## 7. RQ3: Diversity Shift

RQ3는 논문의 가장 중요한 measurement finding 중 하나입니다.

질문은 다음입니다.

> 추천 노출의 다양성이 실제 클릭 소비의 다양성으로 이어지는가?

이 질문은 “추천이 다양했는가?”와 “사용자가 다양하게 소비했는가?”가 다르다는 점을 보여줍니다.

### 7.1 Normalized Entropy

Entropy는 분포가 얼마나 예측 불가능하고 고르게 퍼져 있는지 측정하는 정보이론 지표입니다. 한 category가 거의 모든 비중을 차지하면 다음 항목이 무엇일지 예측하기 쉽습니다. 이때 entropy는 낮습니다. 반대로 여러 category가 비슷한 비중으로 나타나면 다음 항목이 어떤 category일지 예측하기 어렵습니다. 이때 entropy는 높습니다.

가장 기본이 되는 직관은 정보량입니다. 어떤 사건 \(x\)가 일어날 확률이 \(p(x)\)라면 그 사건이 주는 정보량은 보통 다음처럼 씁니다.

\[
I(x)=-\log p(x).
\]

확률이 1인 확실한 사건은 \(-\log 1=0\)이므로 정보량이 0입니다. 이미 확실히 알고 있는 일이 일어나도 새 정보가 없기 때문입니다. 확률이 0.5인 사건은 \(-\log_2 0.5=1\) bit입니다. 확률이 0.25인 사건은 \(-\log_2 0.25=2\) bits입니다. 더 드문 사건일수록 일어났을 때 더 놀랍고, 그래서 정보량이 큽니다.

Entropy는 각 사건의 정보량을 그 사건이 일어날 확률로 가중평균한 값입니다.

\[
H(X)=\sum_x p_x I(x)=\sum_x p_x(-\log p_x)=-\sum_x p_x\log p_x.
\]

여기서 마이너스 기호는 합 밖으로 뺄 수 있습니다. 왜냐하면 \(\sum_x p_x(-\log p_x)\)에서 \(-1\)은 모든 항에 공통으로 곱해지는 상수이기 때문입니다. 그래서 \(-\sum_x p_x\log p_x\)와 같은 식입니다.

\[
E(X)=-\frac{\sum_x p_x\log p_x}{\log |X|}
\]

여기서 \(p_x\)는 category 또는 publisher \(x\)의 share입니다.

Entropy가 높으면 여러 카테고리에 고르게 퍼져 있다는 뜻입니다. Entropy가 낮으면 특정 카테고리에 몰려 있다는 뜻입니다.

분모의 \(\log |X|\)는 정규화 역할을 합니다. 카테고리 수나 publisher 수가 다르면 raw entropy의 최대값도 달라집니다. \(K\)개의 label이 있고 모든 label이 똑같이 \(1/K\)씩 나타날 때 entropy는 최대가 됩니다.

예를 들어 category가 4개이고 각각 0.25씩 나타난다면:

\[
H=-4\times 0.25 \times \log_2(0.25).
\]

\(\log_2(0.25)=\log_2(1/4)=-2\)입니다. 따라서

\[
H=-4\times 0.25\times (-2)=2.
\]

이 값은 \(\log_2 4=2\)와 같습니다. 즉 4개 label이 완전히 균등하면 최대 entropy는 2 bits입니다. 2개 label이면 최대 entropy는 \(\log_2 2=1\), 10개 label이면 \(\log_2 10\approx 3.32\)입니다. 가능한 label 수가 많을수록 raw entropy의 최대값이 커집니다.

그래서 normalized entropy를 씁니다.

\[
H_{\text{norm}}=\frac{H}{\log K}.
\]

여기서 \(H\)는 실제 관측된 분포의 entropy이고, \(K\)는 그 분포에서 비교 기준으로 쓰는 label 수입니다. 본 원고에서는 nonzero support, 즉 실제로 probability가 0보다 큰 observed labels를 기준으로 정규화합니다. 이를 \(\mathcal{K}^+\)처럼 쓸 수 있습니다. 이 기호는 “K plus” 또는 “positive-probability support”라고 읽으면 됩니다. 전체 taxonomy에 category가 15개 있어도 어떤 사용자의 클릭에 Politics, Economy, Sports 세 개만 나타났다면, 그 사용자의 클릭 분포에서 positive support는 세 개입니다.

정규화의 목적은 “label 수가 많아서 entropy가 커진 것”과 “실제로 더 고르게 퍼져서 entropy가 커진 것”을 구분하는 것입니다. Publisher/source는 가능한 label 수가 category보다 훨씬 많습니다. 따라서 raw entropy만 비교하면 publisher entropy가 더 큰 이유가 정말 더 다양한 소비 때문인지, 아니면 가능한 publisher label이 많기 때문인지 헷갈릴 수 있습니다. \(H/\log K\)는 각 분포의 최대 가능 entropy에 비해 실제 entropy가 어느 정도인지 보여줍니다. 1에 가까울수록 가능한 support 안에서 거의 균등하고, 0에 가까울수록 한 label에 몰려 있습니다.

우리 raw 결과는 다음과 같습니다.

- recommendation-category entropy: 0.8352
- click-category entropy: 0.5401
- recommendation-publisher entropy: 0.9129
- click-publisher entropy: 0.6256

이 결과만 보면 logged exposure는 넓고, click consumption은 좁습니다. 즉, 추천 리스트는 다양한 카테고리를 보여주지만, 사용자는 클릭에서 더 좁게 소비하는 것처럼 보입니다.

하지만 여기서 바로 결론을 내리면 안 됩니다. 추천 노출은 클릭보다 item 수가 훨씬 많습니다. 관측 수가 많으면 entropy가 높아질 가능성이 큽니다. 그래서 count matching이 필요합니다.

이 지점이 RQ3의 핵심적인 학문적 조심성입니다. 많은 추천 다양성 논의는 exposure diversity와 consumption diversity를 같은 방향으로 기대하지만, 실제 로그에서는 두 층위의 관측량이 다릅니다. 추천은 하루에 여러 개가 기록되고, 클릭은 그중 일부 또는 전혀 다른 surface에서 발생합니다. 따라서 raw entropy gap은 플랫폼/사용자 행동의 차이와 측정량 차이가 섞인 값입니다. 본 원고가 count matching을 추가한 이유가 바로 이 혼합을 줄이기 위해서입니다.

Entropy로 말할 수 있는 것은 “한 분포가 다른 분포보다 더 evenly spread되어 있다”는 것입니다. 우리 논문식으로는 “raw logged exposure distributions are more even than observed click distributions” 또는 “after count matching, the entropy gap shrinks substantially”라고 말할 수 있습니다. 하지만 entropy만으로 “사용자가 다양성을 싫어한다”, “추천 시스템이 좁은 소비를 유발했다”, “다양한 노출이 실패했다”, “attention diversity가 성공했다”라고 말하면 과해석입니다. Entropy는 preference, satisfaction, attention, causality를 측정하지 않습니다. 오직 관측된 category share가 얼마나 고르게 퍼져 있는지를 측정합니다.

### 7.2 Top-Category Share

Top-share는 가장 큰 카테고리가 전체에서 차지하는 비율입니다.

\[
TopShare(X)=\max_x p_x
\]

Entropy와 방향이 반대입니다.

- entropy가 높으면 다양성이 높다.
- top-share가 높으면 집중도가 높다.

본 결과는 다음과 같습니다.

- recommendation top-category share: 0.3704
- click top-category share: 0.6928

클릭 소비는 특정 카테고리에 훨씬 더 몰려 있습니다. 이 결과는 “click consumption is more top-heavy”라는 표현으로 요약됩니다.

Figure 3에서는 entropy와 top-share가 서로 다른 방향의 지표라는 점을 명확히 표시합니다. 중간 그래프에서 click 쪽 값이 더 큰 것은 오류가 아니라 concentration metric이기 때문입니다.

### 7.3 HHI Concentration

HHI는 concentration을 측정하는 지표입니다. 원래 산업조직론에서 시장집중도를 측정할 때 쓰인 Herfindahl-Hirschman Index이지만, 확률분포나 category share에도 그대로 적용할 수 있습니다. 핵심은 각 category share를 제곱해서 더한다는 점입니다.

\[
HHI(X)=\sum_x p_x^2
\]

만약 모든 비중이 한 카테고리에 몰려 있으면 HHI가 큽니다. 여러 카테고리에 고르게 분산되면 HHI가 작습니다.

예를 들어 네 category가 완전히 균등하면 \(p=(0.25,0.25,0.25,0.25)\)입니다.

\[
HHI=0.25^2+0.25^2+0.25^2+0.25^2=4\times 0.0625=0.25.
\]

반대로 한 category가 70%를 차지하고 나머지가 10%씩이면 \(p=(0.70,0.10,0.10,0.10)\)입니다.

\[
HHI=0.70^2+0.10^2+0.10^2+0.10^2=0.49+0.03=0.52.
\]

HHI가 0.25에서 0.52로 커진 것은 한 category가 지배적으로 커졌기 때문입니다. 제곱을 하기 때문에 큰 share가 훨씬 더 크게 반영됩니다. 이것이 HHI가 top-heavy concentration에 민감한 이유입니다.

본 결과에서 count-matched HHI gap은 0.082입니다.

이것은 노출과 클릭의 item count를 맞춘 뒤에도 클릭 소비가 더 집중되어 있다는 뜻입니다.

HHI가 entropy와 함께 필요한 이유는 concentration을 더 직접적으로 보기 때문입니다. Entropy도 확률분포의 각 \(p_x\)를 반영하지만, 로그 함수 때문에 전체 evenness를 비교적 부드럽게 봅니다. HHI는 큰 비중을 가진 항목에 제곱을 적용하므로 dominant category나 dominant publisher에 더 민감합니다. 그래서 두 분포의 entropy가 비슷해 보여도 HHI는 다르게 나올 수 있습니다.

예를 들어 \(A=(0.70,0.10,0.10,0.10)\)와 \(B=(0.55,0.35,0.05,0.05)\)를 비교해 봅시다. 두 분포 모두 완전 균등하지 않고 어느 정도 퍼져 있습니다. Entropy는 둘 다 중간 정도로 나옵니다. 그러나 HHI는 \(A\)에서 \(0.70^2=0.49\)가 크게 작동하므로 \(A\)가 더 top-heavy하다는 점을 강하게 잡습니다. 즉 entropy는 “전체적으로 얼마나 퍼져 있는가”를 보고, HHI는 “큰 category가 얼마나 지배적인가”를 더 직접적으로 봅니다.

본 데이터에서 count-matched HHI gap 0.082가 남는다는 것은 단순히 클릭 수가 적어서 다양성이 낮아 보이는 문제가 전부는 아니라는 뜻입니다. 관측 수를 맞춘 뒤에도 클릭 소비 쪽이 더 top-heavy한 구조를 보입니다. 이 결과는 “diversity made available”과 “diversity attended to”가 다를 수 있다는 Discussion의 메시지를 뒷받침합니다.

### 7.4 Jensen-Shannon Divergence

Jensen-Shannon divergence는 두 분포의 모양이 얼마나 다른지 보는 distribution-to-distribution distance입니다. Entropy와 HHI는 각각 하나의 분포만 보고 “이 분포가 얼마나 고른가” 또는 “얼마나 집중되어 있는가”를 계산합니다. 반면 JS divergence는 두 분포를 직접 나란히 놓고 “같은 category support 위에서 같은 모양인가, 다른 모양인가”를 묻습니다.

\[
JS(p,q)=\frac{1}{2}KL(p\Vert m)+\frac{1}{2}KL(q\Vert m),\quad m=\frac{p+q}{2}
\]

Entropy는 한 분포의 넓이를 봅니다. HHI는 한 분포의 집중도를 봅니다. JS divergence는 두 분포가 서로 얼마나 다른지 봅니다.

예를 들어 exposure와 click의 entropy가 비슷해도, exposure는 정치/경제에 분산되어 있고 click은 스포츠/연예에 분산되어 있다면 두 분포는 다릅니다. 이런 차이를 JS가 잡아냅니다.

수식의 \(m=(p+q)/2\)는 두 분포의 평균분포입니다. 예를 들어 \(p=(0.8,0.2)\), \(q=(0.5,0.5)\)라면

\[
m=\left(\frac{0.8+0.5}{2},\frac{0.2+0.5}{2}\right)=(0.65,0.35).
\]

그 다음 \(p\)가 평균분포 \(m\)과 얼마나 다른지 \(KL(p\Vert m)\)로 보고, \(q\)가 평균분포 \(m\)과 얼마나 다른지 \(KL(q\Vert m)\)로 봅니다. 마지막으로 둘을 반반 평균냅니다. 그래서 JS는 어느 한쪽만 기준으로 삼지 않습니다. Exposure를 기준으로 click을 평가하는 것도 아니고, click을 기준으로 exposure를 평가하는 것도 아닙니다. 둘 사이의 중간분포를 기준으로 양쪽이 얼마나 떨어져 있는지를 봅니다.

작은 예시를 더 풀어보면, \(\log_2\) 기준으로

\[
KL(p\Vert m)=0.8\log_2(0.8/0.65)+0.2\log_2(0.2/0.35)\approx 0.079,
\]

\[
KL(q\Vert m)=0.5\log_2(0.5/0.65)+0.5\log_2(0.5/0.35)\approx 0.067.
\]

따라서

\[
JS(p,q)\approx \frac{0.079+0.067}{2}=0.073.
\]

직접 KL만 쓰면 \(KL(p\Vert q)\)와 \(KL(q\Vert p)\)가 서로 다릅니다. 즉 방향성이 생깁니다. 하지만 JS는 평균분포를 기준으로 양쪽을 같은 비중으로 보므로 대칭적입니다.

우리 count-matched JS divergence는 0.471입니다.

이 수치가 중요한 이유는, entropy gap이 count matching 후 줄어들어도 distributional mismatch는 여전히 크다는 것을 보여주기 때문입니다.

JS divergence를 쓰는 이유는 KL divergence보다 비교에 적합하기 때문입니다. KL divergence는 방향성이 있고, 한 분포에서 확률이 0인 항목이 다른 분포에서는 양수일 때 해석이 까다로울 수 있습니다. JS divergence는 두 분포의 평균 \(m\)을 기준으로 양쪽 KL을 평균내기 때문에 대칭적이고, 확률이 0인 항목이 있어도 더 안정적으로 계산됩니다. 그래서 exposure distribution과 click distribution처럼 sparse category가 생길 수 있는 로그 데이터에 적합합니다.

0.471이라는 값은 “노출과 클릭의 넓이가 다르다”보다 더 강한 정보를 줍니다. 노출과 클릭이 비슷한 entropy를 갖더라도 서로 다른 카테고리에 퍼져 있으면 JS는 높게 나옵니다. 따라서 본 결과는 count matching 후에도 소비가 단지 조금 더 좁은 것이 아니라, exposure와 click의 category/publisher distribution shape 자체가 다르다는 것을 보여줍니다.

### 7.5 Count Matching

Count matching은 RQ3에서 가장 중요한 robustness check입니다.

Raw exposure는 클릭보다 item 수가 많습니다. 따라서 raw entropy gap은 단순히 “추천은 많이 관측되고 클릭은 적게 관측된다”는 이유로 생길 수 있습니다.

이를 보정하기 위해 각 사용자의 logged exposure를 사용자의 click count와 같은 수로 downsample합니다.

\[
\Delta_M(u)=M(E'_u)-M(C_u),\quad |E'_u|=|C_u|
\]

여기서 \(E'_u\)는 사용자 \(u\)의 exposure에서 click 수만큼 샘플링한 subset입니다. \(M\)은 특정 metric을 뜻하는 placeholder입니다. 예를 들어 \(M\)에 entropy를 넣으면 entropy gap이 되고, HHI를 넣으면 HHI gap이 되고, top-share를 넣으면 top-share gap이 됩니다. JS의 경우에는 하나의 분포에 적용하는 \(M(X)\)라기보다 \(JS(E'_u,C_u)\)처럼 두 분포를 직접 비교합니다.

여기서 주의할 점은 \(M\)과 JS 수식의 평균분포 \(m\)이 다르다는 것입니다. Count matching 설명의 대문자 \(M\)은 “metric”을 뜻하는 일반 기호입니다. JS 수식의 소문자 \(m=(p+q)/2\)는 두 확률분포의 평균분포입니다.

Gap의 방향도 지표마다 다르게 잡습니다. Entropy는 높을수록 더 다양하므로

\[
\Delta H=H(E'_u)-H(C_u)
\]

처럼 exposure minus click을 씁니다. 값이 양수이면 matched exposure가 click보다 더 diverse하다는 뜻입니다.

반면 HHI와 top-share는 높을수록 더 집중되어 있다는 뜻입니다. 논문에서는 positive gap이 “click consumption이 matched exposure보다 더 narrow/concentrated하다”는 의미가 되도록 방향을 바꿉니다.

\[
\Delta HHI=HHI(C_u)-HHI(E'_u)
\]

\[
\Delta TopShare=TopShare(C_u)-TopShare(E'_u)
\]

그래서 HHI gap과 top-share gap이 양수이면 클릭 소비가 노출보다 더 집중되어 있다는 뜻입니다. 방향을 이렇게 맞춰야 Figure와 Table에서 positive value를 일관되게 “click side is narrower”로 읽을 수 있습니다.

본 결과는 다음과 같습니다.

- broad E-C cohort: entropy gap 0.219, HHI gap 0.167, top-share gap 0.162, JS 0.593
- users with at least 5 clicks: entropy gap 0.032, HHI gap 0.091, top-share gap 0.077, JS 0.483
- audit-eligible cohort: entropy gap 0.025, HHI gap 0.082, top-share gap 0.069, JS divergence 0.471
- users with at least 10 clicks in the separate entropy check: category entropy gap near 0.010

이 결과의 의미는 매우 중요합니다.

첫째, raw entropy gap 전체를 강한 행동 효과로 주장하면 안 됩니다. 일부는 click observation이 sparse하기 때문에 생긴 측정 효과입니다.

둘째, count matching 후에도 concentration과 JS mismatch는 남습니다. 따라서 PEC의 RQ3 결과는 완전히 사라지는 것이 아닙니다. 숫자로 보면 entropy gap은 \(0.219\rightarrow0.032\rightarrow0.025\)로 크게 줄어듭니다. 하지만 HHI는 \(0.167\rightarrow0.091\rightarrow0.082\), top-share는 \(0.162\rightarrow0.077\rightarrow0.069\), JS는 \(0.593\rightarrow0.483\rightarrow0.471\)로 줄어들어도 여전히 꽤 남습니다.

Count matching의 학문적 역할은 보수적 검증입니다. 원고가 raw entropy gap만 제시했다면 “추천은 다양하지만 사용자는 좁게 클릭한다”는 해석이 너무 쉬웠을 것입니다. 하지만 클릭 수가 적으면 어떤 분포든 좁아 보일 수 있습니다. Count matching은 이 반론을 정면으로 받아들여 exposure 쪽 관측 수를 click 쪽에 맞춥니다. 그 후에도 남는 gap만 더 조심스럽게 해석합니다.

따라서 RQ3의 최종 주장은 “사용자가 다양성을 무시한다”가 아닙니다. 더 정확한 주장은 “raw diversity gap의 상당 부분은 관측 수 차이와 관련되지만, count-matched 조건에서도 concentration과 distributional mismatch가 남는다”입니다. 이 점이 논문의 measurement audit 성격을 강화합니다.

가장 안전한 결론은 다음입니다.

> Raw diversity gap의 일부는 클릭 수가 적어서 생긴 측정 효과이지만, count를 맞춘 뒤에도 소비가 더 집중되는 신호는 남는다.

## 8. RQ4: Structured but Bounded Divergence

RQ4는 다음 질문입니다.

> preference-consumption divergence가 관측 가능한 profile-state와 behavior feature에 의해 어느 정도 구조화되어 있는가?

이 모델은 추천 모델이 아닙니다. 생산 환경에서 user targeting을 위한 모델도 아닙니다. 목적은 high-divergence가 완전한 noise인지, 아니면 관측 가능한 패턴이 있는지 확인하는 것입니다.

### 8.1 Label

주요 label은 \(D_u=1-J_u\)를 바탕으로 합니다. median보다 divergence가 높은 사용자를 high-divergence로 분류합니다.

이 label은 preference-consumption 관계에서 정의됩니다. 따라서 profile-state feature를 넣으면 construct와 가깝다는 문제가 있습니다. 논문은 이 점을 숨기지 않고 “bounded diagnostic”이라고 표현합니다.

### 8.2 Feature Boundary

모델에는 다음과 같은 feature가 들어갈 수 있습니다.

- basic profile indicator와 category/source profile-support count
- weighted profile-state의 entropy, max weight, salient preference count
- exposure diversity/count feature
- click count, active click days, timing 등 behavior feature

하지만 leakage를 만들 수 있는 feature는 제외합니다.

- preference-click cosine
- clicked-category weight
- preference-click JS
- realized click alignment를 직접 반영하는 feature

이 경계가 중요합니다. 모델이 label을 그대로 복사하는 것이 아니라, 관측 가능한 profile/behavior 구조가 divergence와 관련 있는지를 보려는 것입니다.

여기서 `num_stated_categories`와 `num_stated_publishers`라는 내부 변수명은 오해하기 쉽습니다. 실제 코드는 explicit-selection field와 weighted-profile field에서 관측된 support 중 더 큰 값을 사용합니다. 따라서 이 둘은 Jaccard를 만드는 explicit stated-set cardinality 그 자체가 아니라 profile-support count입니다. 특히 category support count는 698명에서 모두 13으로 일정해 19명의 empty explicit stated-set 사용자를 식별하지 못합니다.

### 8.3 AUC와 AUPRC

AUC는 모델이 positive user와 negative user를 얼마나 잘 순서화하는지 봅니다. AUC 0.5는 random입니다. AUC가 높을수록 high-divergence user를 더 높은 점수로 놓는 경향이 강합니다.

AUPRC는 positive class에 대한 precision-recall 성능입니다. class imbalance가 있거나 positive 탐지가 중요할 때 의미가 있습니다.

AUC는 threshold 하나를 고정하지 않습니다. 모델 점수의 순서가 얼마나 잘 맞는지 보는 지표입니다. 따라서 “어떤 cutoff로 high-divergence user를 잡을 것인가”보다 “모델이 전반적으로 high-divergence user를 더 위에 놓는가”를 평가합니다. 반면 AUPRC는 positive class를 찾아내는 능력에 더 민감합니다. high-divergence user가 상대적으로 적거나, 높은 점수 구간에서의 precision이 중요할 때 AUPRC가 의미를 갖습니다.

본 결과는 다음과 같습니다.

- basic profile + support counts only: AUC 0.544
- unweighted full model: AUC 0.784
- weighted profile-state only: AUC 0.696
- full audit + weighted profile-state: AUC 0.859, AUPRC 0.861
- 19명의 empty stated-set 사용자를 제외한 full audit: AUC 0.853
- category/publisher profile-support counts를 제거한 full audit: AUC 0.862

이 결과는 weighted profile-state가 강한 audit signal을 갖는다는 뜻입니다. 단순히 사용자가 몇 개 카테고리를 선택했는지가 아니라, profile distribution의 shape이 중요합니다.

하지만 이것을 모델 성능 논문처럼 밀면 안 됩니다. 같은 window에서 label과 feature가 가까운 부분이 있기 때문에, future-window diagnostic과 dense-history check를 함께 봐야 합니다.

여기서 중요한 비교는 full audit + weighted profile-state AUC 0.859와 basic profile/support-count baseline AUC 0.544의 차이입니다. 더 중요한 방어 근거는 empty-state 제외 후에도 AUC가 0.853이고 support count 제거 후에는 0.862라는 점입니다. 즉 headline AUC는 19개의 deterministic empty case나 두 support count에 의해 만들어진 결과가 아닙니다. 그러나 future-window diagnostic과 dense-history checks에서 성능이 낮아지기 때문에, 이 결과는 “강한 예측 모델”이 아니라 “divergence가 관측 가능한 구조를 갖는다”는 audit evidence로 해석됩니다.

### 8.4 Temporal Split

Temporal split은 Jan-Mar feature로 Apr-Jun high-divergence를 예측하는 방식입니다.

본 결과는 AUC 0.731입니다.

Same-window AUC 0.859보다 낮습니다. 이는 자연스럽고 중요한 결과입니다. 시간적으로 분리하면 예측이 더 어려워집니다. 그래도 0.731이면 signal이 완전히 사라진 것은 아닙니다.

정확한 해석은 다음입니다.

> divergence는 구조화되어 있지만, 장기적 forecasting claim으로 과장할 정도는 아니다.

### 8.5 Dense-History Checks

Click이 너무 적은 사용자는 divergence가 불안정하게 나올 수 있습니다. 그래서 click 수가 많은 사용자만 따로 봅니다.

결과는 다음과 같습니다.

- users with at least 5 clicks: AUC 0.698
- users with at least 10 clicks: AUC 0.707

성능이 낮아집니다. 이것은 모델이 특히 sparse-history user에서 쉽게 구분되는 패턴을 잡고 있음을 의미합니다. 그래서 논문은 “structured but bounded”라고 말합니다.

### 8.6 SHAP / Feature Importance

SHAP은 feature가 모델 예측에 얼마나 기여했는지 해석하는 도구입니다.

본 release check에서 가장 큰 feature는 `click_count`였고, mean absolute SHAP은 약 0.076입니다.

이 결과는 high-divergence가 단순 profile 문제만이 아니라 behavior와도 관련 있음을 보여줍니다. 하지만 click_count가 중요하다는 사실은 동시에 주의점이기도 합니다. 관측량이 적거나 많은 것 자체가 divergence 측정에 영향을 줄 수 있기 때문입니다.

그래서 dense-history check와 volume feature ablation이 필요합니다.

## 9. Bootstrap Confidence Interval

Bootstrap은 데이터를 여러 번 다시 샘플링해서 같은 통계를 반복 계산하는 방법입니다.

왜 필요한가?

Entropy gap, hit rate, JS divergence 같은 지표는 단순한 평균 하나로 끝내기 어렵습니다. 사용자마다 클릭 수가 다르고, 추천 수가 다르고, distribution shape도 다릅니다. 이때 parametric standard error를 단순하게 계산하기보다 bootstrap이 실용적입니다.

예를 들어 논문에서는 다음과 같은 uncertainty를 보고합니다.

- date-matched logged-list candidate-pool expectation: 9.13%, 95% CI [8.77%, 9.53%]
- publisher entropy gap: 0.274, 95% CI [0.238, 0.309]

이것은 단순 dashboard number가 아니라 empirical measurement임을 보여줍니다.

Bootstrap의 직관은 “현재 관측된 사용자/이벤트 집합이 가능한 표본 중 하나라면, 비슷한 표본을 다시 뽑았을 때 수치가 얼마나 흔들리는가”입니다. 특히 본 연구처럼 사용자별 클릭 수와 추천 수가 불균등하고, 분포 기반 지표가 많은 경우에는 이론적 표준오차를 간단히 쓰기 어렵습니다. Bootstrap confidence interval은 결과가 단일 표본의 우연한 산물이 아니라 어느 정도 안정적인지 확인하는 데 도움을 줍니다.

예를 들어 candidate-pool same-day expectation의 95% CI가 [8.77%, 9.53%]이고 observed same-day hit가 11.29%라면, observed 값이 date-matched logged-list candidate-pool baseline보다 높다는 해석이 더 안정적입니다. 반대로 어떤 gap의 confidence interval이 0 근처를 크게 포함한다면, 그 지표는 강한 결론으로 쓰기 어렵습니다. 따라서 bootstrap은 결과의 크기뿐 아니라 해석의 신뢰 범위를 함께 보여주는 장치입니다.

## 10. Audit-Eligible Cohort

Audit-eligible cohort는 측정이 어느 정도 안정적인 사용자만 포함하는 하위 집단입니다.

조건은 다음과 같습니다.

- at least five matched clicks
- at least 20 matched recommendation items
- at least two active click days
- at least two stated preference categories

이 조건은 cherry-picking이 아니라 measurement validity filter입니다. 클릭이 하나뿐인 사용자에게 entropy나 Jaccard를 계산하면 값이 너무 불안정합니다. 추천 item이 너무 적어도 exposure distribution이 믿기 어렵습니다.

따라서 audit-eligible cohort는 “좋은 수치를 만들기 위한 필터”가 아니라 “해석 가능한 측정을 위한 필터”입니다.

## 11. 핵심 결과를 가르치는 순서

### 11.1 Finding 1: Preference는 의미 있지만 얕다

근거:

- top-category match 77.22%
- primary mean Jaccard 0.2283 (nonempty-set sensitivity 0.2347)
- category cosine 0.452
- publisher cosine 0.080

설명:

> 사용자의 명시적 선호는 주된 관심 방향은 잡지만, 실제 소비의 전체 폭과 publisher-level 선택까지 완전히 설명하지는 못한다.

### 11.2 Finding 2: Logged exposure는 신호가 있지만 부분적이다

근거:

- same-day hit 11.29%
- candidate-pool baseline 9.13%
- top-5 lift 1.47x
- popularity-aware baseline보다도 높음
- 클릭은 여러 surface에서 발생

설명:

> 추천 로그는 무의미하지 않다. 하지만 전체 노출도 아니고 전체 소비 경로도 아니다.

### 11.3 Finding 3: Diversity shift는 층위 의존적이다

근거:

- exposure entropy 0.8352 vs click entropy 0.5401
- exposure top-share 0.3704 vs click top-share 0.6928
- count-matched HHI gap 0.082
- count-matched top-share gap 0.069
- JS divergence 0.471

설명:

> 추천 리스트는 넓게 분포되어 있어도 실제 클릭 소비는 더 집중될 수 있다. Raw entropy gap의 일부는 관측 수 차이 때문이지만, count matching 후에도 concentration/distribution mismatch가 남는다.

### 11.4 Finding 4: Divergence는 구조화되어 있지만 bounded하다

근거:

- same-window weighted model AUC 0.859
- temporal AUC 0.731
- dense-history AUC 약 0.70

설명:

> preference-consumption divergence는 완전한 noise가 아니다. 하지만 이것을 production forecasting model이나 targeting model로 해석하면 안 된다.

## 12. 자주 생기는 오해와 답변

### 오해 1: Same-day hit 11.29%면 추천 시스템이 나쁜 것 아닌가?

아닙니다. Same-day hit는 CTR이 아닙니다. 클릭된 기사 중 같은 날 추천 로그에서 찾을 수 있는 비율입니다. 이 값은 random보다 높으므로 추천 로그가 신호를 갖고 있음을 보여줍니다. 다만 앱 전체 소비 환경을 모두 설명하지는 못합니다.

### 오해 2: Exposure entropy가 높으면 플랫폼이 다양성을 잘 제공한 것 아닌가?

부분적으로만 맞습니다. Logged exposure는 다양할 수 있습니다. 하지만 click consumption이 더 집중되어 있다면, 플랫폼의 다양성 claim은 어느 층위에서 측정한 것인지 명확히 해야 합니다. Exposure diversity와 consumption diversity는 다릅니다.

### 오해 3: Count matching 후 entropy gap이 줄었으니 RQ3가 약해진 것 아닌가?

오히려 논문이 더 강해집니다. Raw entropy gap을 그대로 밀지 않고, 측정 artifact를 인정했기 때문입니다. Count matching 후에도 HHI, top-share, JS divergence가 남기 때문에 robust claim은 residual concentration/distributional mismatch입니다.

### 오해 4: AUC 0.859가 논문의 핵심인가?

아닙니다. AUC는 RQ4의 diagnostic extension입니다. 논문의 핵심은 PEC framework입니다. AUC는 divergence가 어느 정도 구조화되어 있음을 보여주지만, temporal/dense checks 때문에 bounded claim으로 제한됩니다.

### 오해 5: 단일 앱 데이터라 일반화가 안 되는 것 아닌가?

수치 자체는 일반화하면 안 됩니다. 하지만 framework는 일반화 가능합니다. 다른 플랫폼도 preference, exposure, surface, consumption trace를 갖고 있다면 같은 PEC audit을 적용할 수 있습니다.

## 13. 수업/발표용 설명 흐름

원고 구조를 검토할 때는 다음 순서가 적절하다.

1. 먼저 pipeline assumption을 설명합니다. 사용자가 선호를 말하고, 시스템이 추천하고, 사용자가 클릭한다는 단순 흐름입니다.
2. 실제 모바일 뉴스 앱에서는 이 흐름이 깨진다고 설명합니다. 사용자는 여러 surface를 통해 기사를 소비합니다.
3. P, E, S, C 네 층위를 정의합니다.
4. RQ1에서 preference와 consumption이 얼마나 맞는지 봅니다.
5. RQ2에서 click이 logged recommendation exposure로 trace 가능한지 봅니다.
6. RQ3에서 exposure diversity가 consumption diversity로 이어지는지 봅니다.
7. Count matching을 설명해 raw entropy gap의 일부가 측정 효과임을 인정합니다.
8. RQ4에서 divergence가 구조화되어 있지만 bounded하다는 것을 보여줍니다.
9. 마지막으로 “이 논문은 새 추천 모델이 아니라 measurement audit framework”라고 정리합니다.

## 14. 한 페이지 요약

이 논문은 개인화 뉴스 앱에서 사용자의 명시적 선호, 시스템이 기록한 추천 노출, 앱 surface, 실제 클릭 소비를 분리해서 감사합니다. 사용자의 선호는 주된 관심 방향을 어느 정도 잡지만 실제 소비의 전체 폭을 설명하지는 못합니다. 추천 로그는 candidate-pool과 popularity-aware baseline보다 높은 traceability를 보이지만, 클릭의 많은 부분은 headline, category, home/feed, newsroom, article-detail 같은 다른 surface에서 발생합니다. 추천 노출은 raw entropy 기준으로 클릭보다 다양하지만, count matching을 하면 raw gap의 일부는 관측 수 차이 때문임이 드러납니다. 그럼에도 HHI, top-share, JS divergence 기준으로는 residual concentration/distribution mismatch가 남습니다. 마지막으로 weighted profile-state와 behavior feature는 high-divergence user를 어느 정도 식별하지만, future-window diagnostic과 dense-history check에서 성능이 낮아지므로 production prediction이 아니라 bounded diagnostic signal로 해석해야 합니다. 결론적으로 PEC의 메시지는 명확합니다. Preference, exposure, click은 모두 유용한 신호지만, 서로 대체해서는 안 됩니다.

## 15. 작은 예제로 이해하기

이 섹션은 실제 협업 검토에서 수식을 설명할 때 사용할 수 있는 toy example입니다. 논문 수치를 그대로 계산하는 예제는 아니지만, 각 지표가 무엇을 보는지 직관적으로 이해하는 데 도움이 됩니다.

### 15.1 Jaccard 예제

어떤 사용자가 stated category preference로 다음을 선택했다고 합시다.

\[
P_{cat}(u)=\{\text{Politics}, \text{Economy}, \text{Technology}\}
\]

그 사용자가 실제로 가장 많이 클릭한 상위 3개 카테고리가 다음과 같다고 합시다.

\[
C^{top}_{cat}(u)=\{\text{Politics}, \text{Sports}, \text{Entertainment}\}
\]

교집합은 Politics 하나입니다.

\[
P_{cat}(u)\cap C^{top}_{cat}(u)=\{\text{Politics}\}
\]

합집합은 Politics, Economy, Technology, Sports, Entertainment 다섯 개입니다.

\[
P_{cat}(u)\cup C^{top}_{cat}(u)=\{\text{Politics}, \text{Economy}, \text{Technology}, \text{Sports}, \text{Entertainment}\}
\]

따라서 Jaccard는 다음과 같습니다.

\[
J_u=\frac{1}{5}=0.2
\]

이 사용자는 top-category match 관점에서는 Politics가 들어 있으므로 어느 정도 맞는 것처럼 보일 수 있습니다. 하지만 Jaccard 0.2는 전체 소비 폭이 stated preference와 상당히 다르다는 것을 보여줍니다. 이것이 본 원고에서 top-category match와 Jaccard를 둘 다 쓰는 이유입니다.

### 15.2 Cosine 예제

이번에는 set이 아니라 weighted distribution을 봅니다.

사용자 profile-state가 다음과 같다고 합시다.

\[
p^P_u=(\text{Politics}:0.5,\ \text{Economy}:0.3,\ \text{Sports}:0.2)
\]

실제 click distribution은 다음과 같다고 합시다.

\[
p^C_u=(\text{Politics}:0.4,\ \text{Economy}:0.1,\ \text{Sports}:0.5)
\]

두 분포는 완전히 같지는 않지만, Politics와 Sports를 중심으로 어느 정도 같은 방향을 가집니다. Cosine similarity는 이런 “방향성”을 측정합니다.

본 데이터에서 category cosine 0.452는 완전한 정렬은 아니지만 profile-state가 클릭 방향을 어느 정도 담고 있다는 뜻입니다. 반면 publisher cosine 0.080은 source-level에서는 이 방향성이 매우 약하다는 뜻입니다.

### 15.3 Entropy와 Top-Share 예제

두 사용자 또는 두 layer가 있다고 합시다.

Exposure distribution:

\[
(\text{Politics}:0.25,\ \text{Economy}:0.25,\ \text{Sports}:0.25,\ \text{Culture}:0.25)
\]

Click distribution:

\[
(\text{Politics}:0.70,\ \text{Economy}:0.10,\ \text{Sports}:0.10,\ \text{Culture}:0.10)
\]

Exposure는 네 카테고리에 고르게 퍼져 있으므로 entropy가 높고 top-share는 0.25입니다. Click은 Politics에 70%가 몰려 있으므로 entropy는 낮고 top-share는 0.70입니다.

본 원고의 raw 결과가 바로 이 구조와 비슷합니다.

- exposure category entropy 0.8352: 추천 노출은 비교적 넓게 퍼져 있음
- click category entropy 0.5401: 클릭 소비는 더 좁음
- exposure top-share 0.3704: 추천 노출의 최대 카테고리 비중은 낮음
- click top-share 0.6928: 클릭 소비는 한 카테고리에 더 크게 몰림

따라서 Figure 3에서 entropy와 top-share를 함께 해석할 때는 “높을수록 좋은 방향”이 같지 않다는 점을 명시할 필요가 있습니다.

### 15.4 Count Matching 예제

어떤 사용자에게 추천 노출이 100개 있고 클릭이 5개만 있다고 합시다. 추천 100개는 여러 카테고리를 포함할 가능성이 높고, 클릭 5개는 우연히 한두 카테고리에 몰릴 가능성이 큽니다.

이 상태에서 exposure entropy와 click entropy를 직접 비교하면 exposure가 훨씬 다양해 보일 수 있습니다. 하지만 이것은 실제 행동 차이 때문일 수도 있고, 단순히 관측 수 차이 때문일 수도 있습니다.

Count matching은 exposure 100개 중 5개만 여러 번 샘플링해서 클릭 5개와 비교합니다. 이렇게 하면 “노출과 클릭의 item count가 같았다면 다양성 차이가 얼마나 남는가?”를 볼 수 있습니다.

본 결과에서 raw entropy gap은 컸지만 count-matched gap은 0.032로 줄었습니다. 이것은 매우 중요한 정직한 결과입니다. 논문이 강한 이유는 raw gap을 무리하게 밀지 않고, measurement artifact를 인정한 뒤에도 남는 concentration/JS mismatch를 핵심으로 삼기 때문입니다.

### 15.5 JS Divergence 예제

두 분포가 같은 entropy를 가질 수 있지만 서로 다른 카테고리에 몰려 있을 수 있습니다.

Distribution A:

\[
(\text{Politics}:0.5,\ \text{Economy}:0.5)
\]

Distribution B:

\[
(\text{Sports}:0.5,\ \text{Entertainment}:0.5)
\]

두 분포는 둘 다 두 카테고리에 균등하게 퍼져 있으므로 entropy는 비슷합니다. 하지만 내용은 완전히 다릅니다. 이 차이를 잡는 것이 JS divergence입니다.

본 데이터에서 count-matched JS divergence 0.471은 중요한 신호입니다. Entropy gap이 줄어도 exposure와 click의 distribution shape은 여전히 다르다는 뜻이기 때문입니다.

### 15.6 AUC 예제

AUC는 모델이 high-divergence user와 low-divergence user를 얼마나 잘 순서화하는지 보는 지표입니다.

예를 들어 high-divergence 사용자 1명과 low-divergence 사용자 1명을 무작위로 뽑았을 때, 모델이 high-divergence 사용자에게 더 높은 점수를 주면 성공입니다. 이런 pairwise 성공 확률이 AUC입니다.

AUC 0.5는 랜덤입니다. AUC 0.859는 same-window에서 꽤 강한 구분 신호가 있다는 뜻입니다. 하지만 future-window diagnostic에서 0.731, dense-history에서 약 0.70으로 떨어지므로 이 신호는 bounded합니다.

이 설명을 꼭 붙여야 합니다.

> AUC 0.859는 모델 논문의 headline 성능이 아니라, divergence가 관측 가능한 profile-state와 behavior feature에 의해 구조화되어 있음을 보여주는 audit signal이다.

## 16. 수치별 가능한 주장과 해석 경계

### 16.1 Top-category match 77.22%

말할 수 있는 주장:

> 많은 사용자에게서 가장 많이 클릭한 카테고리는 stated preference 안에 포함된다.

해석 범위를 벗어나는 주장:

> 사용자 선호가 실제 소비를 거의 완벽히 설명한다.

왜냐하면 Jaccard와 publisher alignment가 낮기 때문입니다.

### 16.2 Primary Jaccard 0.2283

말할 수 있는 주장:

> stated preference와 top clicked categories의 전체 overlap은 제한적이다.

해석 범위를 벗어나는 주장:

> 사용자의 preference는 무의미하다.

왜냐하면 top-category match와 weighted cosine은 preference가 여전히 신호를 갖고 있음을 보여주기 때문입니다.

### 16.3 Same-day hit 11.29%

말할 수 있는 주장:

> 클릭의 일부는 같은 날 logged recommendation exposure로 trace 가능하다.

해석 범위를 벗어나는 주장:

> 추천 CTR이 11.29%다.

왜냐하면 이 지표는 impression-to-click 비율이 아니라 click-to-exposure traceability이기 때문입니다.

### 16.4 Top-5 lift 1.47x

말할 수 있는 주장:

> 상위 추천 리스트는 date-matched random보다 클릭된 기사를 더 자주 포함한다.

해석 범위를 벗어나는 주장:

> 추천 알고리즘이 클릭을 47% 증가시켰다.

왜냐하면 lift는 causal effect가 아니라 baseline 대비 traceability ratio입니다.

### 16.5 Count-matched HHI gap 0.082

말할 수 있는 주장:

> 관측 수를 맞춘 뒤에도 클릭 소비는 matched exposure보다 더 집중되어 있다.

해석 범위를 벗어나는 주장:

> 사용자가 다양성을 싫어한다.

왜냐하면 집중의 원인은 사용자 선호, UI 구조, headline salience, breaking news, logging incompleteness 등 여러 가능성이 있기 때문입니다.

### 16.6 JS divergence 0.471

말할 수 있는 주장:

> exposure와 click distribution의 shape이 count matching 후에도 다르다.

해석 범위를 벗어나는 주장:

> 플랫폼이 이념적으로 편향되어 있다.

왜냐하면 본 연구는 article-level ideology label을 사용하지 않았고, category/publisher metadata만 분석했기 때문입니다.

### 16.7 AUC 0.859

말할 수 있는 주장:

> weighted profile-state와 behavior feature는 high-divergence를 same-window에서 잘 구분한다.

해석 범위를 벗어나는 주장:

> 이 모델은 production에서 high-divergence user를 안정적으로 예측할 수 있다.

왜냐하면 future-window diagnostic과 dense-history check에서 성능이 낮아지고, profile snapshot ambiguity가 있기 때문입니다.

## 17. 주요 검토 쟁점과 해석 메모

### 쟁점: 결국 추천이 안 좋다는 말인가?

아닙니다. 이 논문은 추천 품질을 CTR이나 ranking accuracy로 평가하는 논문이 아닙니다. RQ2에서 same-day hit가 candidate-pool baseline보다 높고 top-k lift도 1보다 크기 때문에 logged recommendation exposure에는 분명 signal이 있습니다. 다만 그 signal이 observed click consumption 전체를 설명하지는 않습니다. 이유는 모바일 뉴스 앱이 single-list environment가 아니라 multi-surface environment이기 때문입니다. 따라서 올바른 결론은 “추천이 나쁘다”가 아니라 “logged recommendation exposure is signal-bearing yet partial”입니다.

### 쟁점: Raw entropy gap이 count matching 후 줄었다면 diversity finding이 약해진 것 아닌가?

이 결과는 원고의 측정 해석을 더 정교하게 만든다. Raw entropy gap은 exposure item count가 click count보다 많아서 커질 수 있습니다. 본 연구는 이 문제를 숨기지 않고 count matching으로 보정했습니다. 그 결과 entropy gap은 줄었지만, HHI gap, top-share gap, JS divergence는 audit-eligible cohort에서 남았습니다. 따라서 robust claim은 “raw entropy가 크다”가 아니라 “count correction 후에도 concentration과 distributional mismatch가 남는다”입니다.

### 쟁점: AUC 0.859면 모델 논문으로 가야 하는 것 아닌가?

아닙니다. AUC는 이 논문의 중심 기여가 아니라 RQ4의 diagnostic evidence입니다. High-divergence label 자체가 preference-consumption 관계에서 정의되므로, same-window AUC를 production model 성능처럼 과장하면 위험합니다. 그래서 논문은 future-window diagnostic, dense-history check, direct label-construction feature exclusion을 함께 제시합니다. 결론은 high-divergence가 구조화되어 있지만 bounded하다는 것입니다.

### 쟁점: 왜 attention이라는 단어를 쓰면서 dwell time이 없나?

논문 제목의 “Exposure Is Not Attention”은 큰 문제의식, 즉 노출과 실제 주의/소비가 같지 않다는 것을 표현합니다. 하지만 본문에서는 click consumption이라는 제한된 표현을 씁니다. 본 연구는 dwell time, scroll depth, reading completion이 없다는 한계를 명확히 인정합니다. 따라서 분석 대상은 complete attention이 아니라 observed click consumption입니다.

### 쟁점: 단일 앱이면 일반화가 약한 것 아닌가?

수치 일반화는 조심해야 합니다. 논문도 특정 hit rate나 entropy gap이 다른 플랫폼에서 그대로 나온다고 주장하지 않습니다. 일반화되는 것은 PEC audit protocol입니다. 다른 플랫폼도 preference, exposure, surface, consumption trace를 갖고 있다면 같은 방식으로 각 layer가 alignment되는지, traceability가 어느 정도인지, exposure diversity와 consumption diversity가 어떻게 달라지는지 분석할 수 있습니다.

## 18. 실제 질문을 받았을 때 설명하는 법

이 섹션은 논문을 발표하거나 교수/학생에게 설명할 때 바로 쓸 수 있는 답변 형태로 정리한 것입니다. 위의 수식 설명을 실제 대화형 설명으로 바꾼 버전입니다.

### 18.1 RQ1 Jaccard에서 empty stated-category set은 왜 0인가?

질문을 이렇게 받을 수 있습니다.

> 사용자가 stated preference category를 하나도 갖고 있지 않고 클릭 category만 있다면, Jaccard는 어떻게 되나요?

답은 0입니다. Jaccard는 교집합을 합집합으로 나눕니다.

\[
J(P,C)=\frac{|P\cap C|}{|P\cup C|}.
\]

만약 \(P=\varnothing\)이고 \(C=\{\text{Politics},\text{Economy},\text{Sports}\}\)라면 교집합은 비어 있습니다.

\[
P\cap C=\varnothing.
\]

합집합은 클릭 category 집합과 같습니다.

\[
P\cup C=C.
\]

따라서

\[
J=\frac{0}{3}=0.
\]

이것은 “계산할 수 없어서 제외”하는 경우가 아닙니다. 클릭 category set이 비어 있지 않으면 분모는 0이 아니므로 Jaccard는 정상적으로 정의됩니다. 그래서 최종 원고는 19명의 empty stated-category users를 primary Jaccard에서 \(J_u=0\)으로 포함합니다. 그리고 nonempty-set sensitivity 0.2347은 이 19명을 제외하고 679명만 따로 봤을 때 결론이 크게 달라지지 않는지 확인한 보조 분석입니다.

발표용으로 짧게 말하면:

> Empty stated set은 missing으로 처리하지 않았습니다. 클릭 집합이 비어 있지 않으므로 Jaccard는 0으로 정의됩니다. 전체 698명 결과가 primary이고, 679명 nonempty result는 sensitivity입니다.

### 18.2 Jaccard의 한계는 무엇인가?

Jaccard는 set overlap 지표입니다. 그래서 frequency와 weight를 보지 않습니다.

예를 들어 preference와 click set이 모두 \(\{\text{Politics},\text{Economy}\}\)이면 Jaccard는 1입니다. 하지만 실제 클릭이 Politics 99%, Economy 1%였는지, 둘 다 50%였는지는 구분하지 못합니다. 또한 preference에서 Politics에 높은 weight를 주었는지, Economy에 높은 weight를 주었는지도 반영하지 않습니다.

그래서 본 원고는 Jaccard만 쓰지 않습니다. Top-category match는 dominant orientation을 보고, Jaccard는 set breadth overlap을 보고, weighted cosine은 profile-state weight와 click distribution의 방향성을 봅니다. 이 세 지표가 서로 다른 질문에 답합니다.

### 18.3 Cosine은 클릭한 category만 놓고 계산하는가?

아닙니다. Cosine은 두 벡터가 같은 좌표계 위에 있어야 합니다. 따라서 preference에만 있고 클릭에는 없는 category도 0으로 들어가야 하고, 클릭에만 있고 preference에는 없는 category도 0으로 들어가야 합니다.

예를 들어 가능한 category가 Politics, Economy, Sports, Culture라고 합시다.

Preference vector:

\[
(0.5,0.3,0.2,0.0)
\]

Click vector:

\[
(0.4,0.0,0.6,0.0)
\]

여기서 Economy는 preference에는 있지만 click에는 없으므로 click vector에서 0입니다. Culture는 둘 다 없으므로 둘 다 0입니다. 이렇게 같은 좌표계에서 dot product와 norm을 계산해야 합니다.

만약 클릭된 category만 잘라서 계산하면 preference에는 있었지만 클릭되지 않은 category가 사라져 버립니다. 그러면 mismatch가 과소평가됩니다. 그래서 union/full category coordinate 위에서 zero fill을 하는 것이 중요합니다.

### 18.4 Cosine이 “방향”을 본다는 말은 무슨 뜻인가?

두 벡터 \(a=(1,2)\), \(b=(2,4)\)를 봅시다. \(b\)는 \(a\)를 2배 키운 것입니다. 크기는 다르지만 방향은 같습니다.

\[
a\cdot b = 1\cdot2+2\cdot4=10.
\]

\[
\|a\|=\sqrt{1^2+2^2}=\sqrt5,\quad \|b\|=\sqrt{2^2+4^2}=\sqrt{20}=2\sqrt5.
\]

\[
\cos(a,b)=\frac{10}{\sqrt5\cdot2\sqrt5}=1.
\]

그래서 cosine 1은 “두 벡터의 크기가 같다”가 아니라 “한 벡터가 다른 벡터의 양의 배수라서 방향이 완전히 같다”는 뜻입니다. 우리 논문에서는 profile-state distribution과 click distribution이 category별로 비슷한 방향을 갖는지 봅니다.

### 18.5 Entropy에서 \(\log K\)로 나누는 이유는 무엇인가?

Entropy의 최대값은 label 수에 따라 달라집니다. 2개 label이 균등하면 최대 entropy는 \(\log_2 2=1\)입니다. 4개 label이 균등하면 최대 entropy는 \(\log_2 4=2\)입니다. 10개 label이 균등하면 최대 entropy는 \(\log_2 10\approx 3.32\)입니다.

즉 label 수가 많으면 raw entropy가 더 커질 수 있습니다. Publisher/source는 category보다 가능한 label 수가 많습니다. 따라서 raw entropy를 그대로 비교하면 “정말 더 다양해서 큰 것인지” 아니면 “가능한 label 수가 많아서 큰 것인지”가 섞입니다.

Normalized entropy는 실제 entropy \(H\)를 그 label space에서 가능한 최대 entropy \(\log K\)로 나눕니다.

\[
H_{\text{norm}}=\frac{H}{\log K}.
\]

이렇게 하면 값이 0과 1 사이로 해석됩니다. 1에 가까우면 해당 support 안에서 거의 균등하게 퍼져 있고, 0에 가까우면 한두 label에 집중되어 있습니다.

### 18.6 Entropy가 줄었는데 왜 HHI/top-share/JS를 계속 보는가?

Entropy는 within-distribution evenness를 보는 지표입니다. 한 분포가 얼마나 고르게 퍼져 있는지 봅니다. 하지만 entropy 하나만으로는 “어떤 category가 지배적인지”, “두 분포가 같은 category에 퍼져 있는지”를 충분히 알기 어렵습니다.

HHI는 큰 share에 제곱을 적용하므로 top-heavy concentration에 민감합니다. Top-share는 가장 큰 category 하나가 차지하는 비중을 직접 봅니다. JS divergence는 exposure와 click 두 분포의 전체 shape이 서로 같은지 다른지를 봅니다.

그래서 RQ3에서 entropy gap이 줄어든 것은 중요한 사실이지만, 그것만으로 diversity mismatch가 사라졌다고 결론 내릴 수 없습니다. 실제로 audit-eligible cohort에서 entropy gap은 0.025까지 줄어들지만, HHI gap 0.082, top-share gap 0.069, JS divergence 0.471은 남습니다.

### 18.7 Raw group과 count-matched group을 비교하는 것이 취지인가?

취지는 단순히 “raw group과 matched group 중 어느 쪽이 맞는가”를 고르는 것이 아닙니다. 더 정확히는 raw에서 보이는 exposure-click diversity gap이 관측 수 차이 때문에 과장된 것인지 확인하는 것입니다.

넓은 E-C cohort에서는 다음과 같습니다.

| cohort | entropy gap | HHI gap | top-share gap | JS |
|---|---:|---:|---:|---:|
| broad E-C cohort | 0.219 | 0.167 | 0.162 | 0.593 |
| click >= 5 | 0.032 | 0.091 | 0.077 | 0.483 |
| audit-eligible | 0.025 | 0.082 | 0.069 | 0.471 |

여기서 보이는 흐름은 명확합니다. Entropy gap은 \(0.219\rightarrow0.032\rightarrow0.025\)로 크게 줄어듭니다. 따라서 raw entropy gap의 상당 부분은 exposure item count가 click count보다 많아서 생긴 sparse-observation effect와 관련됩니다.

하지만 HHI/top-share/JS는 줄어들어도 완전히 사라지지 않습니다. 따라서 최종 주장은 “raw entropy gap이 크다”가 아니라:

> Count correction 후에도 click consumption은 matched exposure보다 더 concentrated되어 있고, exposure와 click의 distributional shape mismatch가 남는다.

입니다.

### 18.8 Click >= 5 cohort와 audit-eligible cohort의 차이는 무엇인가?

Click >= 5 cohort는 matched clicks가 적어도 5개 있는 사용자입니다. 이 조건은 “클릭이 너무 적어서 분포 계산이 거의 의미 없어지는 사용자”를 줄이기 위한 최소 click-history 조건입니다. 이 cohort의 사용자 수는 count-matched diversity analysis에서 284명입니다.

Audit-eligible cohort는 더 엄격합니다. 최종 원고 기준으로 다음 조건을 추가로 만족해야 합니다.

- at least five matched clicks
- at least 20 matched recommendation items
- at least two active click days
- at least two stated preference categories

이 cohort는 251명입니다. 즉 click >= 5 cohort는 느슨한 안정성 조건이고, audit-eligible cohort는 preference, exposure, behavior 측정이 모두 어느 정도 가능한 더 보수적인 core sample입니다.

두 그룹을 비교하는 목적은 “어느 그룹이 더 좋은가”가 아닙니다. 느슨한 조건에서 보이는 결과가 더 엄격한 조건에서도 남는지 확인하는 robustness logic입니다.

### 18.9 RQ3를 한 문장으로 설명하면?

가장 정확한 한 문장은 다음입니다.

> Raw logs에서는 logged exposure가 click consumption보다 훨씬 다양해 보이지만, count matching을 하면 entropy gap의 상당 부분은 줄어든다. 그럼에도 HHI, top-share, JS 기준의 concentration and distributional mismatch는 audit-eligible cohort에서도 남는다.

교수에게 더 짧게 말하면:

> We do not overclaim the raw entropy gap. Count matching shows much of it is observational, but concentration and distributional mismatch remain.

한글로는:

> Raw entropy 차이를 그대로 행동 효과로 밀지 않고, 관측 수 차이를 보정한 뒤에도 남는 집중도와 분포 모양의 불일치를 핵심 결과로 삼았습니다.

### 18.10 이 결과가 왜 논문을 더 강하게 만드는가?

만약 논문이 raw entropy gap만 보여주고 “추천은 다양하지만 사용자는 좁게 클릭한다”고 주장했다면 Reviewer는 쉽게 반박할 수 있습니다.

> 클릭 수가 추천 노출 수보다 훨씬 적으니까 클릭 분포가 좁아 보이는 건 당연한 것 아닌가?

본 원고는 이 반론을 피하지 않고 count matching으로 직접 검사합니다. 그리고 entropy gap이 실제로 크게 줄어든다는 불리한 결과를 인정합니다. 대신 그 후에도 HHI/top-share/JS mismatch가 남는다는 더 보수적인 결과를 최종 claim으로 삼습니다.

이것이 논문을 강하게 만드는 이유입니다. 강한 말을 줄이고, 살아남는 근거만 남겼기 때문입니다. PEC는 “추천이 다양성을 망쳤다”는 논문이 아니라, “preference, exposure, surface, consumption을 같은 것으로 보면 audit conclusion이 왜곡된다”는 measurement audit 논문입니다.

# Daqiush 2/1 — Slam Agreements

Recorded: 2026-10-22 (Asia/Shanghai)
Status: owner-supplied design record; not executable yet.

This extends [Daqiush 2/1](13_daqiush_2over1.md), including competitive and
preemptive contexts beyond the initial uncontested 1NT scope. All original notes
are retained below. Explicit contextual exceptions must remain distinguishable;
neither conventional familiarity nor the old Meow profile supplies missing rules.

## 1. Authoring structure

| Module | Owner-supplied behavior to represent | Important context / pending decisions |
| --- | --- | --- |
| Ordinary control bidding | Normally second-round-or-better control; skipped unbid suits deny control; voluntary cues promise two extra strength points when possible | Define the reference range and "if possible"; forced cues after an uncapped partner call promise no extras |
| Partner's long suit / shortage | Immediate cue of partner's long suit requires an honor (even Q can qualify); shortage cues wait until level five; immediate repeat after showing a singleton shows a void | Define "immediate", what Q holdings qualify, and explicit priority over ordinary skip-denial inference |
| Minor-trump cue choice | Three-way choice between a three-level cue, four-level cue, and 4m differs from a two-way choice; strong hands may start low, except unstable auctions | Requires exact candidate-set/auction definition, including the named 1NT transfer-then-3D exception |
| Critical-suit controls | Critical suit cannot ordinarily be skipped; own suit can; strong/weak roles create stated exceptions | Define role evidence, opponent suit, unique unbid suit and strength-show count |
| Compressed cue space | With two cue suits the lower cue need not show control; with one, cue shows slam interest without control promise; uncertain trumps can give multiple meanings | Preserve ambiguity instead of prematurely setting a trump or control fact |
| 5M invitations | Voluntary raise invites trump quality; voluntary unilateral 5M is a general slam invitation; an opponent suit can change it to a control request | Need criteria distinguishing raise, unilateral, forced and competitive cases |
| Forcing Pass | Can invite slam, including pass/double/pull patterns | Needs exact legal competitive contexts; does not override the existing right-hand-opponent-Pass Axiom restriction |
| Serious 3NT / 3S | Major fit plus forcing context (or an identified no-NT context) makes the bid conventional; hearts use 3S and 3NT shows S control | Define serious/inferred continuation obligations and shortage/control exceptions; retain the explicitly supplied minor-transfer exception |
| Roman keycard | Useful-void responses, Q/K handling, grand-slam invitations, direct third-round-control asks, enemy-suit stopper asks | Base four-step answer mapping, Q ask recognition, useful void eligibility and precedence remain to be confirmed |
| Interference over 4NT ask | D0P1 with the supplied P/+1 and X/+2 notation; DOPE when too high | Exact mappings and transition threshold required; do not silently substitute a textbook convention |
| Exclusion keycard | Jump above 4S, void suit; five-step answers and specified Q/K continuations | Define applicable prefixes, useful void/safety tests, and boundary treatment at 5NT; opponents' joint strength changes meaning to invitation |
| Preempt keycard | After 2m/3m preempt, 4om asks; 0/1/1.5/2/2.5 steps; after zero next step asks Q; 4NT quantitative | Clarify half-keycard notation, exact asking applicability and continuations |
| Quantitative NT | 4NT invites 6NT nonforcing; minimum Pass, waiting/shape and ace-count replies; later 5NT signoff and six-level fit probes | Imported glyphs require confirmation; scope conflicts with previously specified special 4NT branches require explicit precedence |
| Strong action over preempt | Control-count step responses; major cue responses and natural 4oM exception | Define reference auctions, control counting and exact step maps |
| Two-suit keycard / 5NT | Supplied six-step two-suit keycard responses; multiple possible 5NT purposes | Define combined keycards/queens, triggering context and how the 5NT meanings are distinguished |
| Grand-slam invitation after asking | Skipped lower suits do not need K; higher unvisited suits remain unknown, so K permits counter-invitation only | Preserve required / not-required / unknown distinction rather than treating unknown as absence |

## 2. Confirmed follow-up answers

- Ordinary RKCB uses 1430: 5C=1/4, 5D=0/3, 5H=2 without trump Q,
  5S=2 with trump Q. The supplied void responses remain separate conditional
  alternatives whose eligibility still requires precision.
- Below the five-level trump threshold, Pass is the first ordinary response
  step (1/4); the original source specifies double as the second step. The
  normal-step interpretation is retained, with detailed remaining legal-step
  handling still to be confirmed as needed.
- If the interfering bid is at or above five of the agreed trump suit, use DOPE.
  The owner corrected the parity interpretation: O=Odd and E=Even, i.e.
  **Double=Odd, Pass=Even**. Do not use the reversed mapping suggested in an
  earlier clarification question.
- The owner requests implementing the slam framework alongside 1NT training,
  because those training auctions can reach slam. Do not defer their continuations
  merely because the first reference slice begins with 1NT.
- Slam decisions generally use sampled-deal simulation rather than a single
  point threshold. **Exception:** when considering 6NT with balanced hands and
  poor suit fit, the owner allows point counting: the partnership needs at
  least **33 combined raw HCP** to pursue 6NT. This threshold is specific to
  that balanced, poorly fitting notrump case; it is not a point ceiling for
  choosing Texas versus Jacoby or a replacement for suit-slam simulation.

### Jacoby-transfer splinter and short-suit invitations — owner update

After a Jacoby transfer to a major is accepted **without a superaccept**, a
responder who wants to explore slam may make one of the following six single
jumps in a new suit, all below 4M. The bid shows a singleton or void in that
suit (a splinter) and **immediately agrees the transferred major as trumps**:

| Ordinary transfer sequence (opponent passes omitted) | Splinter calls |
| --- | --- |
| `1NT–2D–2H` | `3S`, `4C`, `4D` (hearts agreed) |
| `1NT–2H–2S` | `4C`, `4D`, `4H` (spades agreed) |

The opener adjusts **raw HCP** for wasted values in the shown short suit,
then responds according to the adjusted strength:

| Adjusted opener strength | Response specified by owner |
| --- | --- |
| Below 15.5 | Return to 4M (including exactly 15, which the owner does not expect in current examples) |
| 15.5–16 | Make a cue bid |
| 16.5–17 | Bid 4NT to ask for keycards with the agreed major as trumps |

The owner gave the following **retained effective point values** for holdings
in the splinter suit: `A = 4`, `AQ/AQJ = 5`, `AK = 6`,
`AKQ or more = 7`, `K/KJ = 1`, `KQ or more = 1.5`, and no A/K = 0.
Adjusted strength is raw HCP less that suit's ordinary HCP, plus its retained
effective value. A 15.5–16 hand may cue past 4M when necessary. Six splinter
meanings, immediate trump agreement and the opener's adjusted responses are
now executable as a historical-auction slice. The responder's automatic choice
to enter a splinter remains disabled until the sampled-deal slam evaluator can
identify slam interest; the owner specified at least six cards in the
transferred major for that future choice. The bounded Jacoby initiation,
ordinary acceptance, confirmed superaccepts and four ordinary 1430 keycard
answers are now executable. Other cue-bid continuations remain outside this slice.

After **any** of the eight confirmed Jacoby superaccepts, all responder hands
already assigned a slam-exploration route bid `4NT` immediately to ask keycards
for the transferred major. A singleton or four-card second suit does not change
that call after superaccept. Currently the automatic selector can establish
this intent only for the approved six-card-major HCP and relative K–R quality
classes; five-card-major hands can transfer, but their later slam classification
and continuations are still unimplemented. After ordinary acceptance, the
previously recorded 4M invitation, splinter and second-suit routes retain
their distinct meanings and await the sampled-deal selector.

Trump agreement is planned as a [seventh axiom](11_axioms.md) alongside the
current six. It will distinguish unset, provisional and agreed trumps; the
meaning of a call that resolves a provisional trump is determined with the
transition order documented there. The privileges of an agreed trump are
profile-defined. Daqiush presently assigns 4NT to ask for the agreed trump's
aces/keycards and fourth-level new suits to control cues. This splinter branch
goes directly to agreed H or S; its 4NT asks keycards for that major. The
generic provisional-state transition and checks are not yet executable.

### Additional trump-agreement boundaries — owner update

Daqiush need not derive trump agreement for auctions that cannot reach a slam.
Agreement is a reference suit for later convention calls, not a commitment to
play that suit. In particular, an agreed minor may still lead to 3NT or to a
natural search for a major. An explicitly natural continuation overrides the
ordinary fourth-level-new-suit-as-control-cue interpretation and does not by
itself erase the earlier minor agreement.

Only when no authored continuation is available should a final-placement
fallback use the agreed suit as evidence and try to place the contract in one
step. The final denomination may instead be NT. Agreement must not short-circuit
a defined natural or conventional continuation. Choosing between the suit and
NT, and choosing the final level, belongs to sampled-deal simulation. Until
that evaluator is available, an uncovered Daqiush auction remains blocked.
The current engine's cheapest-legal-agreed-suit fallback is not this rule;
the Daqiush profile currently blocks uncovered auctions before it runs.

At `1NT–4C–4H` (opponents passing), responder's confirmed next choices are
**Pass** to play 4H or **4NT** to ask for heart keycards. Direct 6H was not
included in the owner's answer. The owner subsequently corrected the timing:
**do not run a new 4H-versus-6H binary decision at this point**. Texas must
have been selected earlier for a game-only route or a slam-if-keycards route;
the responder's later Pass/4NT follows that intent. Simulation for Texas versus
Jacoby belongs to the earlier responder choice and must consider intermediate
contracts and information-gathering continuations, not only the completion
rates of 4H and 6H. After an unambiguous keycard answer, the asker's saved
purpose places five or six of the agreed major and partner passes. Branches
requiring a trump-queen inquiry, a void response, or an unreachable five-level
signoff remain blocked pending specific agreements.

South African Texas immediately agrees its target major: `1NT–4C` agrees hearts
and `1NT–4D` agrees spades. The currently executable calls already write this
major to `agreed_suit` on the initial Texas call.

In minor Stayman, `1NT–2C–2D–4C` asks about minor suits; the inquiry itself does
not agree one. The owner has specified these continuations (opponent passes
omitted):

| Continuation | Public meaning | Agreement reached |
| --- | --- | --- |
| `…–4D` by opener | Four clubs | None yet |
| `…–4D–4H` by responder | Four diamonds | None yet |
| `…–4D–4S` by responder | Also four clubs | Clubs: at least eight together |
| `…–4D–4H–4S` by opener | Also four diamonds | Diamonds: at least eight together |

Once an eight-card minor fit is established in these branches, agree that minor
immediately. Other minor-Stayman continuations are not inferred from this table.

The owner also specified `1NT–2D–2H–3D–3S` as **diamonds agreed**. Responder's
subsequent `4H` is natural even though a fourth-level new suit would usually be
a cue after agreement. Diamond agreement persists; opener's later `4NT` asks
keycards for diamonds, even if the partnership was still exploring hearts.

For other short-suit invitations, the owner supplied the parallel principle:
after adjusting for wasted values in the shown short suit, a hand is weak if
its adjusted strength is at or below the applicable lower bound; otherwise it
is not weak. The lower bound belongs to the active invitation/auction context
and must be established before the rule becomes executable.

## 3. Implementation interpretation constraints

The current executable slice recognizes heart and spade Texas 4NT asks after
either +1 or +2 answer, no-shortage Stayman-fit 4NT asks, six Jacoby-splinter
4NT asks, eight Jacoby-superaccept 4NT asks, and the diamond-fit ask after a
natural 4H. For these uncontested prefixes it can
answer ordinary RKCB 1430:
5C = 1/4, 5D = 0/3, 5H = 2 without the trump queen, 5S = 2 with it. A hand
with a void does not take an ordinary answer while the special void branch is
unimplemented. An asker's private keycard purpose resolves the ordinary
answer to a five- or six-level final placement when the missing count is
unambiguous; other continuations still require explicit rules.
At `1NT–4C–4H`, a responder who chose game-only Texas follows the saved purpose
and Passes; the selector does not make a fresh binary 4H-versus-6H decision.

These are engineering constraints on recording the agreements, not extra bidding
agreements introduced by the implementer:

- Resolve the active convention and explicit exceptions before deriving public
  meaning. Do not first record a generic control promise and later leave it in
  state when a compressed-space or partner-suit exception removes that promise.
- Keep separate evidence for controls, additional strength, trump agreement,
  trump quality, keycards, queen, and requested kings. An invitation or cue may
  convey only some of these.
- Evidence is seat-owned and grounded in the public auction. "Extra two points"
  must not read partner's actual hand or silently double-count previously shown
  strength. Its baseline and consumption/reset rules require confirmation.
- Natural, splinter, control-cue, serious, keycard, quantitative, retransfer and
  grand-slam-invitation meanings are context-dependent. The same printed call
  must not acquire all of them at once merely because multiple broad modules fit.
- When more than one applicable convention still conflicts, report the ambiguity
  and obtain clarification. Simulation can compare agreed alternatives, but cannot
  define what the partners agreed a call means.
- Implement the shared slam framework alongside the 1NT slice. Supported training
  auctions must continue through the required slam branches. Competitive/preemptive
  methods can be exercised from their specified prefixes without implying that
  all preceding opening/competitive systems have been authored. Unresolved
  meanings still require clarification, not generic replacement conventions.

## 4. Clarification register

Section 2 resolves S06's base answer map and S08's DOPE threshold/parity. Their
other contextual details remain open; the original question wording is retained
below for traceability.

| ID | Missing precision / question |
| --- | --- |
| S01 | Define the additional-strength baseline, the unit of two points (HCP, K-R or other), "if possible", and how previously shown extras are consumed. Which public condition establishes an uncapped call that forces a cue? |
| S02 | Which Q holdings can immediately cue partner's long suit? Which prior shortage bid and turn count make a repeat show a void? Does the no-skip-denial exception apply only to this immediate repeat? |
| S03 | Enumerate three-choice/two-choice minor auctions and unstable exceptions; define strong/weak role thresholds, "only one chance to show strength", extreme fit, and how critical suits are identified when several candidates exist. |
| S04 | Supply precise auctions for the two-cue/one-cue rules and their forcing status. How are the stated 5M/enemy-suit/new-suit three-way meanings selected, and what distinguishes voluntary raise versus unilateral 5M? |
| S05 | Specify serious-3NT/3S applicability when NT is excluded, the return obligation, and how missing controls end exploration. Confirm how it interacts with the earlier 1NT–Stayman spade counter-invitation and minor-transfer exception. |
| S06 | What is the ordinary Roman-keycard four-step answer map? Define useful voids, conditions preventing keycard/Q misunderstanding, and the eligibility for replacing ordinary answers with 5NT/6-suit answers. |
| S07 | Resolve the apparent overlap between new-suit king-showing after a void reply and "any rebid is a grand-slam invitation" after 5NT/6X/6Y. Does a call have both attributes, or do separate contexts take priority? What does `5ª` denote? |
| S08 | Spell out interference responses: D0P1 versus the supplied `P=+1,X=+2`, DOPE answer map, and what level/remaining room switches the method. |
| S09 | For exclusion, does "above 4S" include 4NT and all later jumps, and in which agreed-trump contexts? Does exactly 5NT belong to the grand-slam-only branch? Give a concrete answer sequence including the void-suit ace counted as K. |
| S10 | Define preempt 1.5/2.5 answers and two-suit `25无/低/高/有`, including which kings/queens are counted and which suit is low/high. Confirm control-count weights and the strong-over-preempt triggering auctions. |
| S11 | Confirm imported `5§`, `5¨`, `5ª` glyphs, quantitative waiting/ace steps, and scope of "whenever a forcing raise exists, 4NT is always quantitative" relative to explicit RKCB exceptions. |
| S12 | Define the exact nonforcing-RKCB branch `1NT–2C–2X–3m–3NT–4m–4NT`: which hands may Pass and which must answer? Do not treat this as ordinary forcing keycard by default. |
| S13 | Give contexts distinguishing the three 5NT meanings (choose trumps, top honors, all first-round controls) and 1/2/3 versus 0/1/2 responses. Define counter-invitations for unknown required kings. |

## 5. Original owner notes — preserved verbatim

```text
四、满贯叫牌

扣叫1：扣叫的花色有第二轮以上控制（A/K/单/缺），越过的未叫花色否认控制，每次扣叫承诺2点额外实力（如果可能有）。但同伴无上限叫品强迫扣叫，此种扣叫当然不保证任何额外实力。1. 立刻扣同伴长套必须是大牌（甚至可以Q），单缺留到5阶再扣。2. 叫完单张后立刻再扣原花色是缺门，不否认其他控制。对于低花将牌，3阶扣叫、4阶扣叫、4m三选一时，3阶扣叫弱（但强牌若有3阶花色控制也由3阶花色起步，除非进程特殊：1NT-2H-2S-3D这样的不稳定进程）；二选一时，4m弱。  
扣叫2：不能越过关键花色控制（唯一未叫或敌方）。可以越过自己花色控制。明确强对弱、强牌可以越过控制去扣关键控制的上一个花色、弱牌只能示强一次则可以越过其他花色控制扣关键控制。  
扣叫3：因故只有两门可扣，扣低的不保证控制。只有一门时，扣叫单纯表示满贯兴趣（区别于直接封局）[例如1S (3D) 4D; (2S) 3H 3S]，不承诺控制；若将牌也还模糊，扣叫可能是多义（可能要自己的将，也可能要同伴的将）；将牌为高花、空间紧张而有关键花色时，5M、越过4M扣叫分别否认/承诺控制，但敌方极配时改为弱/强（默认有控制），还有新花可扣时5M、敌花、新花分别为只缺控制、只缺总量、缺控制和总量。
例：Q：19点6M322，其中3是Axx，希望看到这门单缺有满贯的牌怎么试探？A：引导希望对家主动扣叫这门，是不是单缺不清楚，后面可能还需要5M邀请总量。
自愿加叫5M邀请将牌质量（三顶有二上6，三顶都有6阶扣叫）；自愿独叫5M满贯综合邀请；但若敌方叫一套，为要求一个敌花控制（见扣叫部分）
逼叫性pass有时用于邀请满贯，包括下一口就是满贯、自己pass同伴加倍后自己改回。
严肃3NT：若在3NT以下已经找到高花配合且已经建立逼局进程（或已找到9张配等不可能打3NT的进程），则3NT（H为将牌时改为3S，而3NT为S控制）为约定叫，表示要求同伴扣叫，此次扣叫后除非缺控制，否则发起人将再次扣叫查看情况。相应地，存在严肃3NT时的扣叫要求同伴只有在有额外实力时才继续扣叫。特例：自然体系1NT-2S/NT-3C/D-3NT=严肃性，后续开叫人低限4m、高限扣叫（见扣叫部分）。
罗马关键张问叫：5NT：0、2或4个关键张，有一个有用的空门；6阶新花，表示1或3个关键张加一个有用的空门（空门低于将牌），6阶将牌表示1或3个关键张加一个有用的空门（空门高于将牌），答叫空门需要保证关键张、将牌Q不被误会，且答空门后同伴6阶新花均为答K而非问K；5ª若不为问Q，为转移至5NT——止叫或再叫6阶展示K。在4NT问叫后得到5NT/6X/6Y答叫，此时不再具体问将牌Q或边花K，任何再叫均为大满贯邀请（若越过某个花色，表示不需要该花色的K）。罗马关键张后直接再叫6阶低于将牌的花色为询问第三轮控制，但若为敌方花色则改为问止张。
1NT-2C-2X-3m-3NT-4m-4NT是不逼叫的罗马关键张问叫。
4NT问叫被干扰，空间允许时使用D0P1(P=+1,X=+2)，过高则DOPE
除外关键张问叫：4S以上跳叫为缺门关键张问叫，所跳花色为缺门，要求同伴答其它花色的关键张（0/3，1/4无Q，1/4有Q，2无Q，2有Q）后续：得到0/3答叫，+1问Q，（5NT以下）+2问K；得到5NT以下的1/4答叫，+1问K（同伴缺门花色的A算作K）；得到5NT以上的答叫，任何再叫均为大满贯邀请（若越过某个花色，表示不需要该花色的K）。此种跳叫要求有相应阶数满贯把握。敌方联手示强后改为缺门满贯邀请。
阻击关键张：2/3m阻击后，4om阻击关键张，答叫：0/1/1.5/2/2.5，0后加级问Q；4NT自然邀请
示量邀请：不同于有将进程下的逼叫性问A，无将进程下，4NT为示量邀请6NT，是不逼叫的。同伴的再叫：pass=低限，5§=有未表示的额外牌型，对6NT有疑问，请同伴答A数量（14/03/2）；5¨-5ª=答A数量（14/03/2）。答A后，同伴5NT止叫，6阶花色对套（具体几张取决于叫牌进程）。一些进程下，直接示量邀请可能否认止张：1C(2C)4NT；2C2D(2S)4NT；1C1H2D4NT。存在逼叫的加叫，则4NT一律为示量邀请。
对阻击争强单套满贯兴趣：按控制数加级试探满贯：1-，2，3，4+。对高花争强扣叫，按控制数加级试探满贯：4D，4M，4NT：3-4，5+有控制，5+无控制[4oM仍为自然]
敌方示强后满贯叫牌的变化：同伴阻击争叫2M，4m仍为配合显示叫但取消满贯邀请；敌方示强，缺门关键张变为缺门满贯邀请
双套关键张：14/03/25无/25低/25高/25有
5NT可能的含义：选将牌、或问顶张（1/2/3或0/1/2）、或（同伴扣控制或5M后）第一轮控制齐全
问A后邀请大满贯，越过的（更低）花色不要K，未达的（更高）花色未知是否要K所以有K只能反邀。
```

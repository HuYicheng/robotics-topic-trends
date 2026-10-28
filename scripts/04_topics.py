"""Topic rules (title regexes, case-insensitive) and the paper x topic matrix.

A paper can match several topics. Rules are matched on titles only: every source has titles in the same
form, abstracts are not uniformly available. Recall is limited to papers that name the topic in the title;
trends are comparable as long as that naming habit is stable (terminology drift is flagged in the report).
Output: data/topic_matrix.csv, results/precision_samples/<topic>.txt (random matched titles for review)
"""
import csv
import os
import random
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

# (topic, family, regex)
TOPICS = [
    # A. learning methods and models
    ("VLA / robot foundation models", "A learning", r"vision[- ]language[- ]action|\bvlas?\b|robot(ic)? foundation models?|generalist (robot(ic)? )?(polic(y|ies)|agents?)|foundation polic|large behavio(u)?r models?|\bopenvla\b|\brt-2\b|\brt-x\b|\bπ0|\bpi[_-]?0\b"),
    ("LLM / VLM", "A learning", r"large language models?|\bllms?\b|\bvlms?\b|vision[- ]language models?|multi-?modal (large )?language models?|\bmllms?\b|\bgpt\b|\bgpt-|chatgpt|language models?"),
    ("Language grounding / open-vocabulary", "A learning", r"language[- ](conditioned|guided|driven|instructed|grounded)|natural language(?! processing)|open[- ]vocabulary|instruction[- ]following|language instructions?|(?<!non-)(?<!non)(?<!non )\bverbal\b|\btext[- ](guided|conditioned)"),
    ("Diffusion / flow generative models", "A learning", r"(?<!anisotropic )(?<!label )(?<!advection[-– ])(?<!reaction[-– ])(?<!convection[-– ])(?<!thermal )(?<!heat )(?<!gas )(?<!chemical )(?<!molecular )(?<!pheromone[-– ])(?<!distributed )(?<!resilient )(?<!intermittent )(?<!information )(?<!considerable )(?<!maximum )(?<!drift and )(?<!drift[- ])(?<!hypergraph )(?<!smoke )(?<!release and )(?<!distance )(?<!id-based )diffusion(?![- ]based path planning| distance| with the\b| process(es)? governed| of\b|[- ](tensor|weighted|mri|coefficients?|equations?|terms?\b))|flow[- ]matching|rectified flow|score[- ]based (diffusion|generative|models?|polic)|consistency (models?|polic)|denoising (diffusion|score|process|polic)"),
    ("Other generative models", "A learning", r"\bgenerative|variational auto-?encoders?|\bvaes?\b|\bgans?\b|adversarial networks?|autoregressive|normali[sz]ing flows?"),
    ("Imitation learning / LfD", "A learning", r"\bimitation|behaviou?r(al)? cloning|learning from (human )?demonstrations?|\blfd\b|demonstrations?(?! videos?\s*(\(|:|is\b|are\b|can\b|at\b|was\b|were\b|and (the )?(source )?code|please|https?|of (our|the) (results|experiments|system|method|approach|proposed|robot)))|apprenticeship"),
    ("Reinforcement learning", "A learning", r"reinforcement learning|\b(deep )?rl\b|policy optimi[sz]ation|policy gradients?|\bppo\b|actor[- ]critic|q[- ]learning|\brewards?\b|reward (shaping|design|learning|model)"),
    ("Sim-to-real", "A learning", r"sim[- ]?(to|2)[- ]?real|real[- ]?(to|2)[- ]?sim|domain randomi[sz]ation|reality gap"),
    ("World models / video prediction", "A learning", r"(?:learn\w*|latent|deep|generative|neural|imagin\w*|dream\w*|predict\w*|videos?|train\w*|fine-?tun\w*|model-based|pre-?train\w*|foundation models?|diffusion|action-conditioned|self-supervised|reinforcement|\brl\b|autoregressive|transformer|token\w*|agents?|driving|dynamics?|simulat\w*|embodied|visuo\w*|visual|pixels?|polic(?:y|ies)|gaussian|3dgs|4d|future|rollouts?|physics)[^.;]{0,150}?(?<!real-)(?<!real )(?<!semantic )(?<!spatial )(?<!reliable )(?<!abstract )world[- ]?model(?:s|l?ing)?|(?<!real-)(?<!real )(?<!semantic )(?<!spatial )(?<!reliable )(?<!abstract )world[- ]?model(?:s|l?ing)?[^.;]{0,150}?(?:learn\w*|latent|deep|generative|neural|imagin\w*|dream\w*|predict\w*|videos?|train\w*|fine-?tun\w*|model-based|pre-?train\w*|foundation models?|diffusion|action-conditioned|self-supervised|reinforcement|\brl\b|autoregressive|transformer|token\w*|agents?|driving|dynamics?|simulat\w*|embodied|visuo\w*|visual|pixels?|polic(?:y|ies)|gaussian|3dgs|4d|future|rollouts?|physics)|video (generation|prediction|diffusion|world models?|generative models?)|generative (video|simulation)"),
    ("Learning from human video / human-to-robot transfer", "A learning", r"human[- ](hand )?videos?|human (play|demonstration) videos?|internet[- ](scale )?videos?|in-the-wild videos?|human[- ]to[- ](robot|humanoid)(?! (object )?hand-?over)|egocentric human|human egocentric|video demonstrations?(?!\s*(\(|:|is\b|are\b|can\b|at\b|was\b|were\b|and (the )?(source )?code|please|https?|of (our|the) (results|experiments|system|method|approach|proposed|robot)|of learned))|videos? of humans"),
    ("Teleoperation (incl. data-collection interfaces)", "A learning", r"tele-?operat|data[- ]collection|\bumi\b|universal manipulation interface|puppeteer|(bilateral|haptic|teleoperat\w*) leader[- ]follower|leader[- ]follower (bidirectional|bilateral|arms?\b|robotic surgical|haptic|teleop\w*|interfaces?\b|devices?\b|setup|master)"),
    ("Datasets / benchmarks", "A learning", r"\bdatasets?\b|\bbenchmarks?\b|benchmarking"),
    ("Reasoning / chain-of-thought", "A learning", r"\breasoning\b|\breason (about|over|through|across)\b|ability to reason|chain[- ]of[- ]thought|\bthink(ing)?\b"),
    ("Cross-embodiment", "A learning", r"cross[- ]embodiment|embodiment[- ](agnostic|transfer|independent)|multi[- ]embodiment|across ([\w-]+ (and|,) )*embodiments|(different|diverse|multiple|many|various|varied|heterogeneous|distinct|new|novel|unseen) (robot |robotic )?embodiments|embodiment[- ](gap|mismatch)"),
    ("3D Gaussian splatting", "A learning", r"gaussian splatting|\b3dgs\b|splat(?!planner)"),
    ("NeRF / neural implicit fields", "A learning", r"nerfs?\b|neural radiance|radiance fields?|neural (implicit|fields?)|implicit neural|feature fields?"),
    ("Mamba / state-space sequence models", "A learning", r"\bmamba\b"),
    ("Self-supervised / pretraining / representation", "A learning", r"self[- ]supervised|representation learning|contrastive|pre-?train|unsupervised"),
    ("Graph neural networks", "A learning", r"graph neural|\bgnns?\b|graph networks?|graph attention"),
    # B. platforms and domains
    ("Humanoid robots", "B platform", r"humanoid"),
    ("Legged robots / locomotion", "B platform", r"legged|quadruped|biped|hexapod|locomotion"),
    ("Aerial robots / UAV", "B platform", r"\buavs?\b|\buas\b|\bdrones?\b|quadrotors?|quadcopters?|multi-?rotors?|multicopters?|aerial(?! (phases?|reorientation))|\bmavs?\b|flying|(?<!time-of-)(?<!time of )\bflights?\b(?![- ]phases?)|fixed[- ]wing|\bvtol\b|ornithopter|flapping"),
    ("Autonomous driving", "B platform", r"autonomous driving|self[- ]driving|\bdriving\b|autonomous vehicles?|ego[- ]vehicle|\blanes?\b|highway|parking|mixed traffic|traffic (scenes?|scenarios?|participants?|agents?|lights?|signs?|accidents?|interactions?|flow|simulation)|road users?|\bbev\b|bird.?s[- ]eye[- ]view|nuscenes|\bcarla\b|waymo"),
    ("Underwater / marine", "B platform", r"underwater|\bmarine|\bauvs?\b|\brovs?\b|subsea|ocean|aquatic|\bships?\b|(surface|unmanned|autonomous|marine|maritime) vessels?|maritime|\bboats?\b|surface vehicles?|seabed|seafloor|\bsonar\b"),
    ("Space robotics", "B platform", r"(?<!task-)(?<!task )(?<!joint-)(?<!joint )(?<!configuration )(?<!operational )\bspace robot|spacecraft|planetary (surface|explor|rover|terrain|analog|mission|robot|uav|perspective)|lunar|\bmoon\b|(?<!hku-)\bmars\b(?![- ]lvig)|martian|\bon-orbit|\bin-orbit|orbital (servic|robot|debris|assembly)|microgravity|free-flying|asteroid|satellite (servic|captur|robot|docking)|space station|extraterrestrial"),
    ("Mobile manipulation", "B platform", r"mobile manipulat"),
    ("Whole-body control / loco-manipulation", "B platform", r"whole[- ]body|loco-?manipulation"),
    ("Soft robots", "B platform", r"\bsoft[- ]?(robot|actuat|grip|bod|material|manipulat|sens|continuum|finger|hand|skin|arm|crawl|swim|machine|exo|wearable)|soft-bodied|continuum robots?|origami|pneumatic|artificial muscles?|hydrogel|elastomers?|kirigami|tensegrity"),
    ("Micro / bio-inspired robots", "B platform", r"micro-?robots?|nano-?robots?|magnetic(ally)?[- ](actuat|driven|guided|steer|control|soft)|bio-?inspired(?! (sensors?|cameras?|vision|event))|bio-?hybrid|insect|\bfish\b(?![- ]?eye)|bird[- ](inspired|like)|\bavian|(?<!in vivo )animal(?!s? (experiments?|studies|study|models?|trials?|tissues?|subjects?|testing|tests?|cadavers?)\b)"),
    ("Multi-robot / multi-agent / swarms", "B platform", r"(?<!mixed )multi[- ]robots?(?! (pretraining|pre-training|rollouts?|data|datasets?))|swarms?|multi[- ]agent|\bfleets?\b(?![- ](data|mean))|teams? of robots|robot teams?|heterogeneous robots|\bcollective (behaviou?r|motion|transport|intelligence|decision|perception|construction)|decentrali[sz]ed (multi|control|coordination|planning|estimation|collision)"),
    ("Wearable / exoskeleton / prosthesis / rehab", "B platform", r"exoskeleton|exosuit|prosthe|wearable|orthos[ie]s|orthotic|rehabilitat(?!es\b)|assistive(?! agents?)"),
    ("Surgical / medical", "B platform", r"surg|medical|endoscop|catheter|laparoscop|\bneedles?\b|ultrasound|biopsy|minimally invasive|intravascular|clinical|patients?\b|endoluminal|colonoscop|bronchoscop"),
    ("Agriculture / field", "B platform", r"agricultur|(?<!random )(?<!image )(?<!a )(?<!derive )(?<!derived )\bcrops?\b(?! of the)(?! (scale|size|regions?|around))|(?<!energy )(?<!power )(?<!solar )harvest(?!ing (energy|power|solar|electricity|ambient))|orchard|\bfarm|\bweeds?\b|forestry|forest (environments?|canopy|inventory|monitoring|terrain|ecosystems?|floor)|(in|through|under) (the |a |dense )?forests?\b|field robot|greenhouse|phenotyp|fruit (picking|harvest|detection|ripeness|counting|orchard)|fruit-picking|livestock|cattle|vineyard|plant (root|leaf|leaves|disease|stem|organ|growth)"),
    ("Industrial / logistics / construction", "B platform", r"industrial|manufactur|\bfactory\b|\bfactories\b|warehouse|logistic|welding|machining|\bconstruction (sites?|robots?|machine|machinery|industry|automation|tasks?|equipment|work)|building construction|robotic construction|\binspection\b|bin[- ]picking|palleti[sz]|\bparcels?\b"),
    # C. tasks and capabilities
    ("Manipulation (any)", "C task", r"manipulat"),
    ("Grasping", "C task", r"grasp"),
    ("Dexterous / in-hand", "C task", r"dexter|\bin[- ]hand\b|multi[- ]finger|anthropomorphic hand|robot(ic)? hands?\b|five[- ]finger"),
    ("Bimanual", "C task", r"bimanual|bi-manual|dual[- ]arm|two[- ]arm|two[- ]handed"),
    ("Deformable objects", "C task", r"(?<!non-)deformable(?:(?:,| and| or| and/or|/)(?: and| or)? ?[\w-]+)? (linear |thin |elastic |soft |planar |3d |fragile |articulated |volumetric )?(objects?|items?|bags?|packages?|materials?|cloth|fabrics?|garments?|ropes?|cables?|food|parts?|workpieces?|containers?|sheets?|tissues?|dlos?|shells?|plastics?|object manipulation)|\bcloth\b|clothes|garments?|(fabric|textile)s? (manipulation|folding|unfolding|handling|smoothing)|(rope|cable|wire)s? (manipulation|routing|insertion|knot|tying|shaping|untangling)|linear objects?|\bdlos?\b|wire harness|dough|elasto-?plastic|\bbags?\b(?![- ]of)|knot[- ]tying"),
    ("Contact-rich / assembly", "C task", r"contact[- ]rich|(?<!self-)(?<!user )\bassembl(y|ing)\b(?! (study|time|instructions?))|peg[- ]in[- ]hole|(connector|part|object|robotic|peg|tight) insertion|insertion (tasks?|polic|skills?)|screw(ing|driving)\b|non-?prehensile|\bpushing\b|contact[- ]implicit"),
    ("Articulated objects / affordance", "C task", r"articulated objects?|affordance"),
    ("Tactile sensing", "C task", r"tactile(?! (walking|paving))|visuo-?tactile|gelsight|\btouch(ing)?\b|e-skin|electronic skin|slip detection"),
    ("Haptics", "C task", r"haptic"),
    ("Navigation", "C task", r"navigat|\bvln\b|object[- ]goal|autonomous exploration|frontier[- ]based|frontier[- ](exploration|detection|selection|cells?|goals?|points?|regions?|extraction|nodes?|targets?|maps?)|(exploration|unexplored|unknown|explored) frontiers?|frontiers? (between|of the (known|explored|unexplored))|frontiers?\b(?! of research)(?=[^.;]{0,120}?(?:explor\w*|\bmaps?\b|mapping|unmapped|voxels?|grids?\b|cells?\b|unknown|unexplored|unobserved|occupan\w*|free[- ]space|information gain|coverage))|(?:explor\w*|\bmaps?\b|mapping|unmapped|voxels?|grids?\b|cells?\b|unknown|unexplored|unobserved|occupan\w*|free[- ]space|information gain|coverage)[^.;]{0,120}?frontiers?\b(?! of research)"),
    ("Long-horizon / task planning / TAMP", "C task", r"long[- ]horizon|task and motion planning|task-motion planning|\btamp\b|task planning|\bpddl\b|neuro-?symbolic|symbolic (plan|reason|task)|behaviou?r trees?|hierarchical (task|planning)"),
    ("Human-robot interaction", "C task", r"(?<!paired )(?<!aligned )human[- ]robot(?![- ](data|datasets?|demonstrations?|demos?|pairs?|paired|co-?training|mid[- ]training|alignment|aligned|embodiment|retarget\w*|correspondence|kinematics?|motion (retarget\w*|transfer|mapping)|video))|\bhri\b|social(ly)? (robots?|navigation|aware)|collaborative robots?|\bcobots?\b|(?<!single )(?<!non-)shared (autonomy|control)|human[- ]aware|human[- ]in[- ]the[- ]loop|human feedback|user study|\btrust\b(?![- ](region|calibrated))|older adults|children"),
    ("Perception: detection / segmentation / tracking / pose", "C task", r"(?<!failure )(?<!anomaly )(?<!fault )(?<!slip )(?<!collision )(?<!contact )(?<!error )detection|segmentation|(?<!trajectory )(?<!path )(?<!reference )(?<!motion )(?<!whole-body )(?<!whole body )(?<!humanoid )(?<!teleoperation )tracking(?! (control|polic\w*|controllers?))|pose estimation|(?<!anomaly )(?<!failure )recognition|6d pose|6-?dof pose|^(?!.*(?:humanoid|manipulators?|whole[- ]body)).*\bmotion tracking(?! (?:control|polic\w*|controllers?))|panoptic"),
    ("3D perception / LiDAR / point clouds", "C task", r"lidar|point[- ]?clouds?|occupancy|voxel|depth (estimation|completion|sensing)|3d (detection|reconstruction|perception|scene|mapping|semantic|object)|scene reconstruction"),
    ("SLAM / localization / state estimation", "C task", r"(?:\b|(?<=[a-z]))(?<!is)slam\d*\b|odometry|locali[sz]ation|\bmapping\b|state estimation|place recognition|loop closure|bundle adjustment|visual[- ]inertial|lidar[- ]inertial|\bvio\b"),
    ("Radar / 4D radar", "C task", r"\bradars?\b|mm-?wave|millimeter[- ]wave"),
    ("Event cameras / neuromorphic", "C task", r"(?<!discrete-)(?<!discrete )event[- ](based(?! (control|controllers?|teleoperation|tracking control|pid|simulat|schedul|communicat|trigger|consensus|observer|mpc|model predictive|kalman|pedestrian|behaviou?r))|cameras?|vision|streams?)|neuromorphic|spiking|dynamic vision sensor"),
    ("Prediction / forecasting", "C task", r"trajectory prediction|motion prediction|forecast|intention (prediction|estimation)"),
    # D. classic methods
    ("Motion / path planning", "D method", r"motion plan|path plan|trajectory plan|trajectory generation|\brrt|sampling[- ]based|kinodynamic|collision[- ](free|avoidance)|obstacle avoidance|path[- ]finding|(?<!task )(?<!task-level )(?<!symbolic )(?<!high-level )(?<!high level )(?<!llm )(?<!llm-based )(?<!vlm )(?<!vlm-based )(?<!language )(?<!language-based )(?<!pddl )(?<!classical task )(?<!reasoning )(?<!semantic )\bplanners?\b|(?:\bpaths?\b|trajector\w*|waypoints?)[^.;]{0,60}?\bplanners?\b|\bplanners?\b[^.;]{0,60}?(?:\bpaths?\b|trajector\w*|waypoints?)"),
    ("MPC / optimal control / trajectory optimization", "D method", r"(?<!language )model[- ]predictive|\bmpc\b|\bnmpc\b|\bmppi\b|optimal control|trajectory optimi[sz]ation|\bilqr\b|\bddp\b|(?:quadratic program\w*|\bqp\b|optimi[sz]ation|inverse dynamics|operational[- ]space)[^.;]{0,80}?whole[- ]body control|whole[- ]body control[^.;]{0,80}?(?:quadratic program\w*|\bqp\b|optimi[sz]ation|inverse dynamics|operational[- ]space)|(?:torque[- ]based|hierarch\w*|task[- ]priority|task[- ]space|riccati|computed[- ]torque|model[- ]based)[^.;]*?whole[- ]body control|whole[- ]body control[^.;]*?(?:torque[- ]based|hierarch\w*|task[- ]priority|task[- ]space|riccati|computed[- ]torque|model[- ]based)|convex (optimi[sz]ation|mpc|relaxation|program)"),
    ("Safety / verification", "D method", r"\bsafe|safety|barrier functions?|\bcbfs?\b|reachab(le|ility) (sets?|tubes?|analysis|based|constraints?)|reachability-based|(hamilton[- ]jacobi|\bhj\b|backward|forward) reachab|reach[- ]avoid|reachability games?|formal (methods?|verification|guarantees?|specifications?)|temporal logic|\bltl\b|\bstl\b|certif|shield|\brisk"),
    ("Uncertainty / probabilistic", "D method", r"uncertaint|bayesian|(?<!diffusion )probabilistic(?!(ally)? (complete|completeness|roadmaps?))|gaussian process|stochastic|chance[- ]constrained|\bbelief|particle filter|kalman"),
    ("Force / impedance control", "D method", r"(?<!electrical )impedance(?! tomography)|admittance|force control|compliance control|(?<!whole-body )(?<!whole body )(?<!humanoid )(?<!scene )interaction control|hybrid force|force[- ]feedback|force[- ](aware|controlled|regulation)"),
    ("Hardware: mechanisms / actuators / design", "D method", r"(?<!attention )(?<!neural )(?<!trust )(?<!reward )(?<!incentive )(?<!gating )(?<!memory )(?<!feedback )\bmechanisms?\b|\bactuators?\b(?! (fault|failure|saturation|constraint))|transmission|gearbox|\bgears?\b(?![- ](meshing|insertion|insert|assembly|assemble|peg))|linkage|variable[- ]stiffness|\bfabricat|^design (and|of)\b|: design (and|of)\b|\bdesign, (modeling|modelling|control|fabrication)|parallel (robot|manipulator|mechanism)|modular robots?"),
    ("Calibration / registration", "D method", r"(?<!conformal )(?<!conformal risk )(?<!well-)(?<!well )(?<!poorly )(?<!mis)(?<!un)(?<!over)(?<!under)(?<!risk )(?<!confidence )(?<!uncertainty )(?<!trust-)(?<!preference-)(?<!reliability )(?<!progress )(?<!action )calibrat(?!ion[- ]free)(?!ed (confidence|uncertaint\w*|probabilit\w*|coverage|predict\w*|risk|barrier|spatial belief|belief|measure|scores?|estimates?|gaussian|velocity|sets?|intervals?))(?!ion (samples?|sets?\b|scores?|of (the )?(uncertaint|confidence|predict|probabilit|risk)))(?!es (foundation|representation|observational|prediction uncertaint))|(?:\bun|\bmis|\bwell[- ])calibrat\w*,? (?:and synchronized |[\w-]+ )?(?:cameras?|sensors?|rgb\b|monocular|stereo|videos?|visual[- ](?:servo\w*|feedback)|image-based|eye-in-hand|tactile|robots?\b|feature points?|networks? of|multi-view|lidars?\b|imus?\b)|registration|extrinsic (calibration|parameters)|hand[- ]eye"),
    # E. macro terms (vocabulary indicators, not topics)
    ("[term] learn*", "E term", r"learn"),
    ("[term] neural / deep", "E term", r"\bneural\b|\bdeep\b"),
    ("[term] foundation model", "E term", r"foundation models?"),
    ("[term] language", "E term", r"language"),
    ("[term] zero-shot / generalization / open-world", "E term", r"zero[- ]shot|few[- ]shot|open[- ]world|generali[sz]|unseen"),
    ("[term] transformer / attention", "E term", r"transformer|attention"),
    ("[term] embodied", "E term", r"\bembodied\b"),
    ("[term] real-world", "E term", r"real[- ]world"),
]
COMPILED = [(n, f, re.compile(p, re.I)) for n, f, p in TOPICS]

# Abstract versions of rules whose title words are generic inside abstracts (audit of matched words, 2026-10-14):
# "the dataset", "safely", "mapping X to Y", "anomaly detection", "the uncertainty", "attention mechanism",
# "industrial applications". Other topics use the title rule on the abstract as well.
ABSTRACT_OVERRIDES = {
    "Datasets / benchmarks": r"\bwe (introduce|present|release|propose|collect|construct|build|create|curate|open-source)\w* (a |an |the |our )?((new|novel|large-scale|first|open-source|public|publicly available|real-world|multi-?modal|comprehensive|diverse|challenging|synthetic|annotated|unified)[ ,]+)*(dataset|benchmark)s?\b|(this|our) (paper|work|letter|article) (introduces|presents|proposes|releases) (a |an |the )?([\w-]+ ){0,4}(dataset|benchmark)\b|the proposed (dataset|benchmark)\b|\b(new|novel|first) (large-scale |public |open-source )?(dataset|benchmark) (for|of|that|which|named|called|comprising|containing)\b",
    "Safety / verification": r"safety[- ]critical (control|systems?)|safe (control|reinforcement learning|\brl\b|exploration|navigation|motion planning|planning|sets?|polic(y|ies)|learning|trajector)|safety (filters?|constraints?|guarantees?|certificates?|verification|shield|monitor)|barrier functions?|\bcbfs?\b|reachab(le|ility) (sets?|tubes?|analysis|based|constraints?)|reachability-based|(hamilton[- ]jacobi|\bhj\b|backward|forward) reachab|reach[- ]avoid|reachability games?|formal (methods?|verification|guarantees?|specifications?)|temporal logic|\bltl\b|\bstl\b|runtime (monitor|verification)|shielding|chance[- ]constrained|risk[- ](aware|sensitive|bounded)|collision[- ]free guarantee",
    "SLAM / localization / state estimation": r"(?:\b|(?<=[a-z]))(?<!is)slam\d*\b|simultaneous locali[sz]ation and mapping|odometry|state estimation|place recognition|loop closure|bundle adjustment|visual[- ]inertial|lidar[- ]inertial|\bvio\b|\bpose[- ]graph|global locali[sz]ation|relocali[sz]ation|(robot|vehicle|camera|lidar|visual|map[- ]based|indoor|outdoor|uav|multi-robot) locali[sz]ation",
    "Perception: detection / segmentation / tracking / pose": r"object detection|3d detection|object detector|semantic segmentation|instance segmentation|panoptic|\b(object|multi-object|target|visual|point) tracking|pose estimation|6d pose|6-?dof pose|keypoint detection|object recognition|scene understanding",
    "Uncertainty / probabilistic": r"uncertainty (quantification|estimation|estimates|propagation|modell?ing|-aware|aware)|uncertainty-aware|bayesian|(?<!diffusion )probabilistic(?!(ally)? (complete|completeness|roadmaps?))|gaussian process|kalman|particle filter|belief space|chance[- ]constrained|epistemic|aleatoric",
    "Hardware: mechanisms / actuators / design": r"\bactuators?\b(?! (fault|failure|saturation|constraint))|actuation (system|mechanism|unit|module)|transmission|gearbox|\bgears?\b(?![- ](meshing|insertion|insert|assembly|assemble|peg))|linkage|variable[- ]stiffness|\bfabricat|(?<!visual )(?<!semantic )(?<!class )(?<!patch[- ])(?<!support )(?<!action )(?<!skill )\bprototype(?!s\b)(?!-based)(?! (implementation|learning|network|vectors?|memory|router))|mechanism design|novel mechanism|mechanical design|parallel (robot|manipulator|mechanism)|(?:built|fabricat\w*|manufactur\w*|tested|propulsion|diameters?|\d\s?mm\b|\d\s?cm\b|physical|experiment\w*|hardware|robotic|grippers?|end-effectors?|actuat\w*|developed|prosthe\w*|devices?|mechanis\w*|industrial)[^.;]{0,100}?(?<!visual )(?<!semantic )(?<!class )(?<!patch[- ])(?<!support )(?<!action )(?<!skill )\bprototypes\b|(?<!visual )(?<!semantic )(?<!class )(?<!patch[- ])(?<!support )(?<!action )(?<!skill )\bprototypes\b[^.;]{0,100}?(?:built|fabricat\w*|manufactur\w*|tested|propulsion|diameters?|\d\s?mm\b|\d\s?cm\b|physical|experiment\w*|hardware|robotic|grippers?|end-effectors?|actuat\w*|developed|prosthe\w*|devices?|mechanis\w*|industrial)",
    "Reasoning / chain-of-thought": r"chain[- ]of[- ]thought|reasoning (capabilit|abilit|models?|chains?|traces?|steps?|process)|(spatial|commonsense|common-sense|physical|embodied|multi-?modal|visual|semantic|high-level|logical|causal|temporal|long-horizon|task|geometric|language) reasoning|(llm|vlm|mllm|language model|vision-language model)s?[- ](based |driven )?reasoning|reasoning (and|with) (planning|language|vlms?|llms?)",
    "Teleoperation (incl. data-collection interfaces)": r"tele-?operat|\bumi\b|universal manipulation interface|puppeteer|(bilateral|haptic|teleoperat\w*) leader[- ]follower|leader[- ]follower (bidirectional|bilateral|arms?\b|robotic surgical|haptic|teleop\w*|interfaces?\b|devices?\b|setup|master)|(robot|demonstration|manipulation|teleoperation|real-world robot) data collection|data collection (system|interface|device|setup|pipeline) for (robot|manipulation|imitation|policy)",
    # MPC (2026-10-28): whole-body control counts in abstracts when the paper is optimisation / model based (cue anywhere, no
    # policy-learning word) or has no learning word at all; on titles only with a cue in the same title (tested on 98 removals)
    "MPC / optimal control / trajectory optimization": r"(?<!language )model[- ]predictive|\bmpc\b|\bnmpc\b|\bmppi\b|optimal control|trajectory optimi[sz]ation|\bilqr\b|\bddp\b|(?:quadratic program\w*|\bqp\b|optimi[sz]ation|inverse dynamics|operational[- ]space)[^.;]{0,80}?whole[- ]body control|whole[- ]body control[^.;]{0,80}?(?:quadratic program\w*|\bqp\b|optimi[sz]ation|inverse dynamics|operational[- ]space)|(?:torque[- ]based|hierarch\w*|task[- ]priority|task[- ]space|riccati|computed[- ]torque|model[- ]based)[^.;]*?whole[- ]body control|whole[- ]body control[^.;]*?(?:torque[- ]based|hierarch\w*|task[- ]priority|task[- ]space|riccati|computed[- ]torque|model[- ]based)|convex (optimi[sz]ation|mpc|relaxation|program)|^(?!.*?(?:reinforcement learning|\brl\b|polic(?:y|ies)\b|imitation|motion tracking|behaviou?r cloning|foundation model|distill))(?=.*?(?:quadratic|\bh?qp\b|optimi[sz]|optimal|inverse dynamics|operational[- ]space|task[- ]space|null[- ]space|computed[- ]torque|\blqr\b|riccati|momentum[- ]based|model[- ]based|torque[- ]based|hierarch|priorit|inverse kinematics|sampling[- ]based)).*?whole[- ]body control|^(?!.*?(?:reinforcement learning|\brl\b|polic(?:y|ies)\b|imitation|motion tracking|behaviou?r cloning|foundation model|distill|teleoperat|learn|neural|data-driven|demonstration)).*?whole[- ]body control",
    "Industrial / logistics / construction": r"industrial (robots?|manipulators?|settings?|environments?|assembly|automation|inspection|process|production|tasks?|scenarios?|applications? of robots)|manufacturing (process|tasks?|lines?|systems?|cells?|environments?)|\bfactory\b|\bfactories\b|warehouse|logistic|welding|machining|\bconstruction (sites?|robots?|machine|machinery|industry|automation|tasks?|equipment|work)|bin[- ]picking|palleti[sz]|\bparcels?\b",
}
ABSTRACT_COMPILED = {n: re.compile(ABSTRACT_OVERRIDES.get(n, p), re.I) for n, _, p in TOPICS}

# Sentence-level vetoes (2026-10-28, round 3 of the fixes after the CoRL 2026 review). For these topics, a match whose
# text contains `target` does not count when its sentence has a cue of another sense (`other`; None = always) and no cue
# of the topic's own sense (`own`). The title is one sentence. Applied by kept() in 04 (titles) and 12 (titles, abstracts).
_UNC = (r"conformal|uncertaint\w*|confiden\w*|probabilit\w*|coverage|\bcritics?\b|value[- ]functions?|\bvalues?\b|\bece\b|"
        r"miscalibrat\w*|reliab\w*|credit|\brisks?\b|belief|residuals?|\bscores?\b|over-?confiden\w*|predictive distribution|quantil\w*")
_SENSOR = (r"cameras?|sensors?|\bimus?\b|inertial|lidars?|extrinsic|intrinsic|\brigs?\b|hand[- ]eye|eye[- ]in[- ]hand|tactile|mocap|"
           r"motion[- ]capture|kinematic\w*|encoders?|retarget\w*|actuators?|\bjoints?\b|stereo|projectors?|depth|force[-/ ]torque|e-?skins?|electronic skins?|visual[- ]servo\w*|ultra-wideband|\buwb\b|ranging|"
           r"robots?\b|manipulators?|registration|point[- ]clouds?|checkerboard|markers?|fiducial|apriltags?|odometry|lens|distortion|"
           r"time[- ]?offsets?|synchroni\w*|spatio-?temporal|magnetometer|accelerometer|gyroscope|radars?|thermal|ultrasound|endoscop\w*|"
           r"microscop\w*|laser|tool[- ]center|\btcp\b|hand[- ]eye|end[- ]effector")
_TASK = (r"\bllms?\b|\bvlms?\b|\bmllms?\b|language models?|foundation models?|\bgpt|task[- ](?:level|planners?|planning|plans?)|symbolic|"
         r"pddl|high[- ]level|agentic|\bagents?\b|sub-?goals?|\bskills?\b|instructions?|reasoning|chain[- ]of[- ]thought|"
         r"video (?:planners?|generation|models?)|world models?|\bvlas?\b|vision[- ]language")
_MOTION = (r"\bpaths?\b|trajector\w*|waypoints?|motions?\b|collisions?|kinodynamic|sampling[- ]based|\brrt|configuration[- ]space|"
           r"c-space|obstacles?|footsteps?|local planners?|global planners?|velocit\w*|dynamically feasible|cost[- ]?(?:maps?|functions?)|occupancy|"
           r"maneuver\w*|steering|swept|reachab\w*|joint[- ]space|inverse kinematics|navigat\w*|\broutes?\b")
_HUMAN = (r"\bhumans?\b|\busers?\b|operators?|people|\bpersons?\b|participants?|pedestrians?|\bsubjects?\b|workers?|patients?|"
          r"caregivers?|teammates?|partners?|novices?|clinicians?|surgeons?|drivers?|passengers?|older adults|children|social|"
          r"interaction|collaborat\w*|teleoperat\w*|public|usability|adoption|\bratings?\b|explain\w*|"
          r"robot[- ]assist\w*|trust[- ](?:aware|dynamics|repair)|decision support")
_ASSIST = (r"exoskeleton|exosuit|wearable|prosthe\w*|orthos[ie]s|orthotic|rehab\w*|patients?|disabilit\w*|disabled|impair\w*|"
           r"elderly|older adults|\bage?ing\b|wheelchairs?|\bgait\b|walking aids?|mobility aids?|feeding|daily living|\badls?\b|caregiv\w*|"
           r"stroke|spinal|amput\w*|paraly\w*|(?:people|persons|users|individuals) (?:with|unable|who cannot)|assistive (?:and [\w-]+ )?(?:devices?|technolog\w*|robots?|manipulat\w*|"
           r"robotics|exoskeletons?|gloves?|suits?)|muscle|joint torques? of the (?:user|wearer)|wearer|assistive (?:navigation|gym)|navigation aids?|\beating\b|\bdressing\b|"
           r"\bbathing\b|\bshaving\b|sit[- ]to[- ]stand|stand[- ]to[- ]sit|\bbcis?\b|brain[- ](?:computer|machine)|motor imagery|\beeg\b|\blimbs?\b|\bdaily\b")
_ML = (r"embedding|representation|class(?:es|ification|ifier)?\b(?! of\b)|features?\b|tokens?|\bparameters\b|neural|networks?|learning|"
       r"software|\bros ?2?\b|prototype-level|codebook|cluster\w*|latent|semantic|few-shot|zero-shot|"
       r"transformer|router|mixture|vectors?|memory|datasets?|\bsolv\w*")
_HW = (r"\bbuilt\b|fabricat\w*|manufactur\w*|propulsion|diameters?|\d\s?mm\b|\d\s?cm\b|\d\s?k?g\b|physical|hardware|grippers?|"
       r"end-effectors?|actuat\w*|motors?|prosthe\w*|devices?|mechanis\w*|3d[- ]print\w*|materials?|silicone|pneumatic|tendons?|"
       r"springs?|circuit|\bpcb\b|battery|\blegs?\b|wheels?|fingers?|exoskeleton|soft robot|tested|robotic|developed|\buavs?\b|flight")
VETO = {
    "Calibration / registration": (r"calibrat", _UNC, _SENSOR),
    "Motion / path planning": (r"\bplanners?\b", _TASK, _MOTION),
    "Human-robot interaction": (r"\btrust\b", None, _HUMAN),
    "Wearable / exoskeleton / prosthesis / rehab": (r"assistive", None, _ASSIST),
    "Hardware: mechanisms / actuators / design": (r"prototype", _ML, _HW),
}
VETO_COMPILED = {n: (re.compile(a, re.I), re.compile(b, re.I) if b else None, re.compile(c, re.I)) for n, (a, b, c) in VETO.items()}
_STOP = re.compile(r"(?<!\be\.g)(?<!\bi\.e)[.;!?](?=\s|$)")


def sentence_at(text, pos):
    """The sentence of text that holds position pos (split at . ; ! ? followed by a space or the end)."""
    start = 0
    for m in _STOP.finditer(text, 0, pos):
        start = m.end()
    m = _STOP.search(text, pos)
    return text[start:m.end() if m else len(text)]


TITLE_CONTEXT = {"Wearable / exoskeleton / prosthesis / rehab"}   # a vetoed title match survives when the abstract has an own cue


def kept(name, rx, text, title=False, context=""):
    """Matches of rx in text that survive the topic's sentence veto (all of them when the topic has no veto). A title is
    one sentence; for TITLE_CONTEXT topics the abstract (context) may supply the own-sense cue of a title match."""
    v = VETO_COMPILED.get(name)
    out = []
    for m in rx.finditer(text):
        if v and v[0].search(m.group(0)):
            s = text if title else sentence_at(text, m.start())
            if (v[1] is None or v[1].search(s)) and not v[2].search(s) \
                    and not (title and name in TITLE_CONTEXT and context and v[2].search(context)):
                continue
        out.append(m)
    return out



def load_papers():
    with open(os.path.join(ROOT, "data", "papers.csv")) as f:
        return list(csv.DictReader(f))


def main():
    papers = load_papers()
    names = [n for n, _, _ in COMPILED]
    with open(os.path.join(ROOT, "data", "topic_matrix.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["uid", "venue", "year"] + names)
        for p in papers:
            w.writerow([p["uid"], p["venue"], p["year"]] + [int(bool(kept(n, rx, p["title"], title=True))) for n, _, rx in COMPILED])
    os.makedirs(os.path.join(ROOT, "results", "precision_samples"), exist_ok=True)
    rnd = random.Random(int(os.environ.get('SAMPLE_SEED', '0')))
    # the reviewed draw (results/precision_review.md) stays the same: papers added later (CoRL 2026 from the conference
    # site, 2026-10-28) are left out of it; they get their own check in 12_title_abstract.py
    recent = [p for p in papers if int(p["year"]) >= 2024 and not p["source"].startswith("corl.org/")]
    for n, fam, rx in COMPILED:
        hits = [p for p in recent if kept(n, rx, p["title"], title=True)]
        sample = rnd.sample(hits, min(15, len(hits)))
        safe = re.sub(r"[^A-Za-z0-9]+", "_", n).strip("_")
        with open(os.path.join(ROOT, "results", "precision_samples", f"{safe}.txt"), "w") as f:
            f.write(f"# {n}  ({fam})  matches 2024-2026: {len(hits)}\n")
            for p in sample:
                f.write(f'{p["venue"]} {p["year"]} | {p["title"]}\n')
    print(f"{len(papers)} papers x {len(names)} topics written")


if __name__ == "__main__":
    main()

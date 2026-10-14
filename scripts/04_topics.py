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
    ("Language grounding / open-vocabulary", "A learning", r"language[- ](conditioned|guided|driven|instructed|grounded)|natural language|open[- ]vocabulary|instruction[- ]following|language instructions?|\bverbal\b|text[- ](guided|conditioned)"),
    ("Diffusion / flow generative models", "A learning", r"diffusion|flow[- ]matching|rectified flow|score[- ]based|consistency (models?|polic)|denoising (diffusion|score|models?|process|polic)"),
    ("Other generative models", "A learning", r"\bgenerative|variational auto-?encoders?|\bvaes?\b|\bgans?\b|adversarial networks?|autoregressive|normali[sz]ing flows?"),
    ("Imitation learning / LfD", "A learning", r"\bimitation|behaviou?r(al)? cloning|learning from (human )?demonstrations?|\blfd\b|demonstrations?|apprenticeship"),
    ("Reinforcement learning", "A learning", r"reinforcement learning|\b(deep )?rl\b|policy optimi[sz]ation|policy gradients?|\bppo\b|actor[- ]critic|q[- ]learning|\brewards?\b|reward (shaping|design|learning|model)"),
    ("Sim-to-real", "A learning", r"sim[- ]?(to|2)[- ]?real|real[- ]?(to|2)[- ]?sim|domain randomi[sz]ation|reality gap"),
    ("World models / video prediction", "A learning", r"world models?|world[- ]modell?ing|video (generation|prediction|diffusion|world models?|generative models?)|generative (video|simulation)"),
    ("Learning from human video / human-to-robot transfer", "A learning", r"human[- ](hand )?videos?|human (play|demonstration) videos?|internet[- ](scale )?videos?|in-the-wild videos?|human[- ]to[- ](robot|humanoid)(?! (object )?hand-?over)|egocentric human|human egocentric|video demonstrations?|videos? of humans"),
    ("Teleoperation (incl. data-collection interfaces)", "A learning", r"tele-?operat|data[- ]collection|\bumi\b|universal manipulation interface|puppeteer|leader[- ]follower"),
    ("Datasets / benchmarks", "A learning", r"\bdatasets?\b|\bbenchmarks?\b|benchmarking"),
    ("Reasoning / chain-of-thought", "A learning", r"\breasoning\b|\breason (about|over|through|across)\b|ability to reason|chain[- ]of[- ]thought|\bthink(ing)?\b"),
    ("Cross-embodiment", "A learning", r"cross[- ]embodiment|embodiment[- ](agnostic|transfer|independent)|multi[- ]embodiment|across embodiments|\bany robot\b"),
    ("3D Gaussian splatting", "A learning", r"gaussian splatting|\b3dgs\b|splat"),
    ("NeRF / neural implicit fields", "A learning", r"\bnerfs?\b|neural radiance|radiance fields?|neural (implicit|fields?)|implicit neural|feature fields?"),
    ("Mamba / state-space sequence models", "A learning", r"\bmamba\b"),
    ("Self-supervised / pretraining / representation", "A learning", r"self[- ]supervised|representation learning|contrastive|pre-?train|unsupervised"),
    ("Graph neural networks", "A learning", r"graph neural|\bgnns?\b|graph networks?|graph attention"),
    # B. platforms and domains
    ("Humanoid robots", "B platform", r"humanoid"),
    ("Legged robots / locomotion", "B platform", r"legged|quadruped|biped|hexapod|locomotion"),
    ("Aerial robots / UAV", "B platform", r"\buavs?\b|\buas\b|\bdrones?\b|quadrotors?|quadcopters?|multi-?rotors?|multicopters?|aerial|\bmavs?\b|flying|\bflights?\b|fixed[- ]wing|\bvtol\b|ornithopter|flapping"),
    ("Autonomous driving", "B platform", r"autonomous driving|self[- ]driving|\bdriving\b|autonomous vehicles?|ego[- ]vehicle|\blanes?\b|highway|parking|mixed traffic|traffic (scenes?|scenarios?|participants?|agents?|lights?|signs?|accidents?|interactions?|flow|simulation)|road users?|\bbev\b|bird.?s[- ]eye[- ]view|nuscenes|\bcarla\b|waymo"),
    ("Underwater / marine", "B platform", r"underwater|marine|\bauvs?\b|\brovs?\b|subsea|ocean|aquatic|\bships?\b|(surface|unmanned|autonomous|marine|maritime) vessels?|maritime|\bboats?\b|surface vehicles?|seabed|seafloor|\bsonar\b"),
    ("Space robotics", "B platform", r"space robot|spacecraft|planetary (surface|explor|rover|terrain|analog|mission|robot|uav|perspective)|lunar|\bmoon\b|(?<!hku-)\bmars\b|martian|\bon-orbit|\bin-orbit|orbital (servic|robot|debris|assembly)|microgravity|free-flying|asteroid|satellite (servic|captur|robot|docking)|space station|extraterrestrial"),
    ("Mobile manipulation", "B platform", r"mobile manipulat"),
    ("Whole-body control / loco-manipulation", "B platform", r"whole[- ]body|loco-?manipulation"),
    ("Soft robots", "B platform", r"\bsoft[- ]?(robot|actuat|grip|bod|material|manipulat|sens|continuum|finger|hand|skin|arm|crawl|swim|machine|exo|wearable)|soft-bodied|continuum robots?|origami|pneumatic|artificial muscles?|hydrogel|elastomers?|kirigami|tensegrity"),
    ("Micro / bio-inspired robots", "B platform", r"micro-?robots?|nano-?robots?|magnetic(ally)?[- ](actuat|driven|guided|steer|control|soft)|bio-?inspired(?! (sensors?|cameras?|vision|event))|bio-?hybrid|insect|\bfish\b|bird[- ](inspired|like)|avian|animal"),
    ("Multi-robot / multi-agent / swarms", "B platform", r"multi[- ]robots?|swarms?|multi[- ]agent|\bfleets?\b|teams? of robots|robot teams?|heterogeneous robots|\bcollective (behaviou?r|motion|transport|intelligence|decision|perception|construction)|decentrali[sz]ed (multi|control|coordination|planning|estimation|collision)"),
    ("Wearable / exoskeleton / prosthesis / rehab", "B platform", r"exoskeleton|exosuit|prosthe|wearable|orthos[ie]s|orthotic|rehabilitat|assistive"),
    ("Surgical / medical", "B platform", r"surg|medical|endoscop|catheter|laparoscop|\bneedles?\b|ultrasound|biopsy|minimally invasive|intravascular|clinical|patients?\b|endoluminal|colonoscop|bronchoscop"),
    ("Agriculture / field", "B platform", r"agricultur|\bcrops?\b|harvest|orchard|\bfarm|\bweeds?\b|forestry|forest (environments?|canopy|inventory|monitoring|terrain|ecosystems?|floor)|(in|through|under) (the |a |dense )?forests?\b|field robot|greenhouse|phenotyp|fruit (picking|harvest|detection|ripeness|counting|orchard)|fruit-picking|livestock|cattle|vineyard|plant (root|leaf|leaves|disease|stem|organ|growth)"),
    ("Industrial / logistics / construction", "B platform", r"industrial|manufactur|\bfactory\b|\bfactories\b|warehouse|logistic|welding|machining|\bconstruction (sites?|robots?|machine|machinery|industry|automation|tasks?|equipment|work)|building construction|robotic construction|\binspection\b|bin[- ]picking|palleti[sz]|\bparcels?\b"),
    # C. tasks and capabilities
    ("Manipulation (any)", "C task", r"manipulat"),
    ("Grasping", "C task", r"grasp"),
    ("Dexterous / in-hand", "C task", r"dexter|\bin[- ]hand\b|multi[- ]finger|anthropomorphic hand|robot(ic)? hands?\b|five[- ]finger"),
    ("Bimanual", "C task", r"bimanual|bi-manual|dual[- ]arm|two[- ]arm|two[- ]handed"),
    ("Deformable objects", "C task", r"deformable|\bcloth\b|clothes|garments?|(fabric|textile)s? (manipulation|folding|unfolding|handling|smoothing)|(rope|cable|wire)s? (manipulation|routing|insertion|knot|tying|shaping|untangling)|linear objects?|\bdlos?\b|wire harness|dough|elasto-?plastic|\bbags?\b|knot[- ]tying"),
    ("Contact-rich / assembly", "C task", r"contact[- ]rich|(?<!self-)(?<!user )\bassembl(y|ing)\b(?! (study|time|instructions?))|peg[- ]in[- ]hole|(connector|part|object|robotic|peg|tight) insertion|insertion (tasks?|polic|skills?)|screw(ing|driving)\b|non-?prehensile|\bpushing\b|contact[- ]implicit"),
    ("Articulated objects / affordance", "C task", r"articulated objects?|affordance"),
    ("Tactile sensing", "C task", r"tactile(?! (walking|paving))|visuo-?tactile|gelsight|\btouch(ing)?\b|e-skin|electronic skin|slip detection"),
    ("Haptics", "C task", r"haptic"),
    ("Navigation", "C task", r"navigat|\bvln\b|object[- ]goal|autonomous exploration|frontier"),
    ("Long-horizon / task planning / TAMP", "C task", r"long[- ]horizon|task and motion planning|task-motion planning|\btamp\b|task planning|\bpddl\b|neuro-?symbolic|symbolic (plan|reason|task)|behaviou?r trees?|hierarchical (task|planning)"),
    ("Human-robot interaction", "C task", r"human[- ]robot|\bhri\b|social(ly)? (robots?|navigation|aware)|collaborative robots?|\bcobots?\b|shared (autonomy|control)|human[- ]aware|human[- ]in[- ]the[- ]loop|human feedback|user study|\btrust\b|older adults|children"),
    ("Perception: detection / segmentation / tracking / pose", "C task", r"detection|segmentation|(?<!trajectory )(?<!path )(?<!reference )tracking(?! control)|pose estimation|recognition|6d pose|6-?dof pose"),
    ("3D perception / LiDAR / point clouds", "C task", r"lidar|point[- ]?clouds?|occupancy|voxel|depth (estimation|completion|sensing)|3d (detection|reconstruction|perception|scene|mapping|semantic|object)|scene reconstruction"),
    ("SLAM / localization / state estimation", "C task", r"\bslam\b|odometry|locali[sz]ation|\bmapping\b|state estimation|place recognition|loop closure|bundle adjustment|visual[- ]inertial|lidar[- ]inertial|\bvio\b"),
    ("Radar / 4D radar", "C task", r"\bradars?\b|mm-?wave|millimeter[- ]wave"),
    ("Event cameras / neuromorphic", "C task", r"event[- ](based|cameras?|vision|streams?)|neuromorphic|spiking|\bsnns?\b|dynamic vision sensor"),
    ("Prediction / forecasting", "C task", r"trajectory prediction|motion prediction|forecast|intention (prediction|estimation)"),
    # D. classic methods
    ("Motion / path planning", "D method", r"motion plan|path plan|trajectory plan|trajectory generation|\brrt|sampling[- ]based|kinodynamic|collision[- ](free|avoidance)|obstacle avoidance|path[- ]finding|\bplanners?\b"),
    ("MPC / optimal control / trajectory optimization", "D method", r"(?<!language )model predictive|\bmpc\b|\bnmpc\b|\bmppi\b|optimal control|trajectory optimi[sz]ation|\bilqr\b|\bddp\b|whole[- ]body control|convex (optimi[sz]ation|mpc|relaxation|program)"),
    ("Safety / verification", "D method", r"\bsafe|safety|barrier functions?|\bcbfs?\b|reachab|formal (methods?|verification|guarantees?|specifications?)|temporal logic|\bltl\b|\bstl\b|certif|shield|\brisk"),
    ("Uncertainty / probabilistic", "D method", r"uncertaint|bayesian|(?<!diffusion )probabilistic|gaussian process|stochastic|chance[- ]constrained|\bbelief|particle filter|kalman"),
    ("Force / impedance control", "D method", r"(?<!electrical )impedance(?! tomography)|admittance|force control|compliance control|interaction control|hybrid force|force[- ]feedback|force[- ](aware|controlled|regulation)"),
    ("Hardware: mechanisms / actuators / design", "D method", r"(?<!attention )(?<!neural )(?<!trust )(?<!reward )(?<!incentive )(?<!gating )(?<!memory )(?<!feedback )\bmechanisms?\b|\bactuators?\b(?! (fault|failure|saturation|constraint))|transmission|gearbox|\bgears?\b|linkage|variable[- ]stiffness|\bfabricat|^design (and|of)\b|: design (and|of)\b|\bdesign, (modeling|modelling|control|fabrication)|parallel (robot|manipulator|mechanism)|modular robots?"),
    ("Calibration / registration", "D method", r"calibrat(?!ion[- ]free)|registration|extrinsic (calibration|parameters)|hand[- ]eye"),
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
    "Safety / verification": r"safety[- ]critical (control|systems?)|safe (control|reinforcement learning|\brl\b|exploration|navigation|motion planning|planning|sets?|polic(y|ies)|learning|trajector)|safety (filters?|constraints?|guarantees?|certificates?|verification|shield|monitor)|barrier functions?|\bcbfs?\b|reachab|formal (methods?|verification|guarantees?|specifications?)|temporal logic|\bltl\b|\bstl\b|runtime (monitor|verification)|shielding|chance[- ]constrained|risk[- ](aware|sensitive|bounded)|collision[- ]free guarantee",
    "SLAM / localization / state estimation": r"\bslam\b|simultaneous locali[sz]ation and mapping|odometry|state estimation|place recognition|loop closure|bundle adjustment|visual[- ]inertial|lidar[- ]inertial|\bvio\b|pose[- ]graph|global locali[sz]ation|relocali[sz]ation|(robot|vehicle|camera|lidar|visual|map[- ]based|indoor|outdoor|uav|multi-robot) locali[sz]ation",
    "Perception: detection / segmentation / tracking / pose": r"object detection|3d detection|object detector|semantic segmentation|instance segmentation|panoptic|\b(object|multi-object|target|visual|point) tracking|pose estimation|6d pose|6-?dof pose|keypoint detection|object recognition|scene understanding",
    "Uncertainty / probabilistic": r"uncertainty (quantification|estimation|estimates|propagation|modell?ing|-aware|aware)|uncertainty-aware|bayesian|(?<!diffusion )probabilistic|gaussian process|kalman|particle filter|belief space|chance[- ]constrained|epistemic|aleatoric",
    "Hardware: mechanisms / actuators / design": r"\bactuators?\b(?! (fault|failure|saturation|constraint))|actuation (system|mechanism|unit|module)|transmission|gearbox|\bgears?\b|linkage|variable[- ]stiffness|\bfabricat|\bprototype|mechanism design|novel mechanism|mechanical design|parallel (robot|manipulator|mechanism)",
    "Reasoning / chain-of-thought": r"chain[- ]of[- ]thought|reasoning (capabilit|abilit|models?|chains?|traces?|steps?|process)|(spatial|commonsense|common-sense|physical|embodied|multi-?modal|visual|semantic|high-level|logical|causal|temporal|long-horizon|task|geometric|language) reasoning|(llm|vlm|mllm|language model|vision-language model)s?[- ](based |driven )?reasoning|reasoning (and|with) (planning|language|vlms?|llms?)",
    "Teleoperation (incl. data-collection interfaces)": r"tele-?operat|\bumi\b|universal manipulation interface|puppeteer|leader[- ]follower|(robot|demonstration|manipulation|teleoperation|real-world robot) data collection|data collection (system|interface|device|setup|pipeline) for (robot|manipulation|imitation|policy)",
    "Industrial / logistics / construction": r"industrial (robots?|manipulators?|settings?|environments?|assembly|automation|inspection|process|production|tasks?|scenarios?|applications? of robots)|manufacturing (process|tasks?|lines?|systems?|cells?|environments?)|\bfactory\b|\bfactories\b|warehouse|logistic|welding|machining|\bconstruction (sites?|robots?|machine|machinery|industry|automation|tasks?|equipment|work)|bin[- ]picking|palleti[sz]|\bparcels?\b",
}
ABSTRACT_COMPILED = {n: re.compile(ABSTRACT_OVERRIDES.get(n, p), re.I) for n, _, p in TOPICS}



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
            w.writerow([p["uid"], p["venue"], p["year"]] + [int(bool(rx.search(p["title"]))) for _, _, rx in COMPILED])
    os.makedirs(os.path.join(ROOT, "results", "precision_samples"), exist_ok=True)
    rnd = random.Random(int(os.environ.get('SAMPLE_SEED', '0')))
    recent = [p for p in papers if int(p["year"]) >= 2024]
    for n, fam, rx in COMPILED:
        hits = [p for p in recent if rx.search(p["title"])]
        sample = rnd.sample(hits, min(15, len(hits)))
        safe = re.sub(r"[^A-Za-z0-9]+", "_", n).strip("_")
        with open(os.path.join(ROOT, "results", "precision_samples", f"{safe}.txt"), "w") as f:
            f.write(f"# {n}  ({fam})  matches 2024-2026: {len(hits)}\n")
            for p in sample:
                f.write(f'{p["venue"]} {p["year"]} | {p["title"]}\n')
    print(f"{len(papers)} papers x {len(names)} topics written")


if __name__ == "__main__":
    main()

"""Explicit decision doctrines. These are frameworks, not personality prompts."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SourceReference:
    id: str
    title: str
    author: str
    locator: str
    relevance: str

    @property
    def citation(self) -> str:
        return f"{self.author}, {self.title}, {self.locator}"


@dataclass(frozen=True)
class Doctrine:
    id: str
    name: str
    primary_question: str
    primary_questions: tuple[str, ...]
    principles: tuple[str, ...]
    procedure: tuple[str, ...]
    evidence_preferences: tuple[str, ...]
    failure_modes: tuple[str, ...]
    blind_spots: tuple[str, ...]
    useful_when: tuple[str, ...]
    defer_when: tuple[str, ...]
    sources: tuple[SourceReference, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "name": self.name,
            "primary_question": self.primary_question,
            "primary_questions": list(self.primary_questions),
            "principles": list(self.principles),
            "procedure": list(self.procedure),
            "evidence_preferences": list(self.evidence_preferences),
            "failure_modes": list(self.failure_modes),
            "blind_spots": list(self.blind_spots),
            "useful_when": list(self.useful_when),
            "defer_when": list(self.defer_when),
            "sources": [source.__dict__ | {"citation": source.citation} for source in self.sources],
        }


def _source(id: str, title: str, author: str, locator: str, relevance: str) -> SourceReference:
    return SourceReference(id, title, author, locator, relevance)


_DOCTRINES = (
    Doctrine(
        id="socratic-examination",
        name="Socratic Examination",
        primary_question="What problem are we actually trying to solve?",
        primary_questions=(
            "What evidence supports the framing?",
            "Which assumptions are being treated as facts?",
            "What would prove the preferred account wrong?",
            "What happens if no action is taken?",
        ),
        principles=("Clarify terms before advising.", "Test premises through questions.", "Admit what is not known."),
        procedure=("Restate the claim.", "Expose premises.", "Seek counterexamples.", "Ask what evidence would resolve the issue."),
        evidence_preferences=("Definitions", "first-hand observations", "counterexamples"),
        failure_modes=("Endless questioning", "performative contrarianism", "withholding useful synthesis"),
        blind_spots=("Urgent action", "questions whose answers require specialist evidence"),
        useful_when=("The problem is poorly framed", "participants disagree about basic terms"),
        defer_when=("Immediate safety action is required", "the framing is already well evidenced"),
        sources=(
            _source("plato-dialogues", "Apology", "Plato", "21d-23b", "Awareness of ignorance and examination of claims"),
            _source("plato-dialogues", "Gorgias", "Plato", "454c-461b", "Distinguishing knowledge from persuasion"),
        ),
    ),
    Doctrine(
        id="aristotelian-counsel",
        name="Aristotelian Practical Wisdom",
        primary_question="What is prudent given the particulars of this situation?",
        primary_questions=("What end is being pursued?", "Which particulars change what appropriate action means?", "What action supports long-term flourishing?"),
        principles=("Practical wisdom deliberates well about contingent action.", "Good means must serve worthwhile ends.", "Character and particulars matter alongside rules."),
        procedure=("Clarify the human end.", "Examine particulars and stakeholders.", "Compare means.", "Choose a proportionate action."),
        evidence_preferences=("Concrete particulars", "experienced judgment", "long-horizon effects on people"),
        failure_modes=("Vague appeals to balance", "status-quo moralism", "smuggling preference in as virtue"),
        blind_spots=("Quantitative uncertainty", "adversarial incentives"),
        useful_when=("Values and context matter", "rules underdetermine the choice"),
        defer_when=("Probabilities dominate", "specialist empirical claims are unresolved"),
        sources=(
            _source("aristotle-nicomachean-ethics", "Nicomachean Ethics", "Aristotle", "Book VI, especially 5 and 7-9", "Practical wisdom concerns deliberation about contingent action"),
        ),
    ),
    Doctrine(
        id="stoic-counsel",
        name="Stoic Counsel",
        primary_question="What part of this decision is actually under our control?",
        primary_questions=("Is fear, anger, ego, or status distorting judgment?", "Can we prepare for an unfavorable outcome?", "Are decision quality and outcome quality being confused?"),
        principles=("Distinguish what depends on us from what does not.", "Judge the quality of chosen action, not luck alone.", "Rehearse adversity without surrendering agency."),
        procedure=("Classify controllables.", "Name emotional distortions.", "Choose the worthy controllable action.", "Prepare to accept residual outcomes."),
        evidence_preferences=("Directly controllable actions", "observable commitments", "downside preparations"),
        failure_modes=("Passivity", "emotional suppression", "calling avoidable harm uncontrollable"),
        blind_spots=("Collective power", "distributional consequences"),
        useful_when=("Anxiety or uncertainty is high", "outcomes depend heavily on others"),
        defer_when=("Structural incentives are central", "harm to others requires outcome analysis"),
        sources=(
            _source("epictetus-discourses-enchiridion", "Enchiridion", "Epictetus", "1", "Distinguishing what is and is not up to us"),
            _source("seneca-moral-letters", "Moral Letters", "Seneca", "Letter 13", "Preparing the mind for feared outcomes"),
        ),
    ),
    Doctrine(
        id="machiavellian-realism",
        name="Machiavellian Realism",
        primary_question="What will actors do once their incentives are affected?",
        primary_questions=("Who holds formal and informal power?", "Which coalition can block execution?", "How will reputation and resistance change after action?"),
        principles=("Analyze conduct through incentives and constraints.", "Power includes the capacity to block.", "Political effects continue after formal decisions."),
        procedure=("Map stakeholders and power.", "Model gains and losses.", "Identify blockers and coalitions.", "Design credible commitments."),
        evidence_preferences=("Observed behavior", "resource and authority control", "credible commitments"),
        failure_modes=("Cynicism", "assuming all motives are selfish", "treating description as ethical permission"),
        blind_spots=("Intrinsic motivation", "moral legitimacy", "tail uncertainty"),
        useful_when=("Stakeholders can resist", "incentives change materially"),
        defer_when=("Claims about motives lack evidence", "ethical acceptability is unresolved"),
        sources=(
            _source("machiavelli-prince", "The Prince", "Niccolo Machiavelli", "Chapters XV-XIX", "Effective conduct, reputation, and resistance under political constraints"),
            _source("machiavelli-discourses", "Discourses on Livy", "Niccolo Machiavelli", "Book I", "Institutions, conflict, and durable political orders"),
        ),
    ),
    Doctrine(
        id="clausewitzian-strategy",
        name="Clausewitzian Strategy",
        primary_question="What happens when this plan encounters reality?",
        primary_questions=("What is the actual objective?", "Which friction could prevent execution?", "Where is effort dispersed?", "Which assumptions require ideal execution?"),
        principles=("Strategy must remain subordinate to its objective.", "Friction separates plans from real execution.", "Information is incomplete; preserve adaptability.", "Concentrate effort on decisive factors."),
        procedure=("Restate the objective.", "Trace means to the objective.", "Stress execution assumptions.", "Concentrate effort and reserve adaptability."),
        evidence_preferences=("Operational constraints", "execution history", "dependency and failure-path evidence"),
        failure_modes=("Overplanning", "false precision", "confusing activity with objective", "assuming execution fidelity"),
        blind_spots=("Moral legitimacy", "non-adversarial cooperation"),
        useful_when=("Execution is complex", "information is incomplete", "plans have many dependencies"),
        defer_when=("The objective itself is ethically disputed", "stakeholder welfare dominates execution"),
        sources=(
            _source("clausewitz-on-war", "On War", "Carl von Clausewitz", "Book I, Chapters 1 and 7", "Political purpose, uncertainty, and friction"),
            _source("clausewitz-on-war", "On War", "Carl von Clausewitz", "Book III, Chapters 11-14", "Concentration, economy of force, and reserves"),
        ),
    ),
    Doctrine(
        id="sun-tzu-positioning",
        name="Sun Tzu Positioning",
        primary_question="Can we shape the situation so the hard choice becomes easier?",
        primary_questions=("Where is the information advantage?", "Can timing improve optionality?", "Can direct confrontation be avoided?"),
        principles=("Shape conditions before committing.", "Seek asymmetry and information advantage.", "Preserve options when timing is uncertain."),
        procedure=("Map positions.", "Find avoidable confrontation.", "Improve information and optionality.", "Act at favorable timing."),
        evidence_preferences=("Comparative position", "timing signals", "information asymmetries"),
        failure_modes=("Indefinite maneuvering", "mistaking cleverness for strategy", "undercommitting"),
        blind_spots=("Transparent cooperation", "duties that require direct action"),
        useful_when=("Timing and positioning are malleable", "direct action is costly"),
        defer_when=("Delay compounds harm", "transparency is ethically required"),
        sources=(
            _source("sun-tzu-art-of-war", "The Art of War", "Sun Tzu", "Chapters I, III, and VI", "Assessment, winning without direct contest, and shaping strengths and weaknesses"),
        ),
    ),
    Doctrine(
        id="humean-skepticism",
        name="Humean Skepticism",
        primary_question="What evidence actually justifies these beliefs?",
        primary_questions=("Which claims are observations and which are inferences?", "What causal story is merely habitual?", "What evidence would reduce uncertainty?"),
        principles=("Separate observation from inference.", "Causal confidence must not outrun evidence.", "Custom can masquerade as knowledge."),
        procedure=("Classify claims.", "Trace evidence for causal links.", "Seek counterevidence.", "Calibrate confidence."),
        evidence_preferences=("Repeated observation", "counterexamples", "explicit provenance"),
        failure_modes=("Paralysis", "demanding certainty", "flattening stronger and weaker evidence"),
        blind_spots=("Urgency", "normative ends"),
        useful_when=("Confidence rests on assumptions", "causal claims drive the decision"),
        defer_when=("A moral value choice remains after facts are settled", "waiting is more costly than error"),
        sources=(
            _source("hume-enquiry", "An Enquiry Concerning Human Understanding", "David Hume", "Sections IV-V", "Limits of causal inference and the role of experience"),
        ),
    ),
    Doctrine(
        id="bayesian-analysis",
        name="Bayesian Analysis",
        primary_question="How should the evidence change our confidence?",
        primary_questions=("What are the competing hypotheses?", "What are the priors?", "Which evidence has the greatest information value?", "What outcomes have the highest expected value?"),
        principles=("Represent uncertainty explicitly.", "Update confidence when diagnostic evidence arrives.", "Prefer information whose expected value exceeds its cost."),
        procedure=("Define hypotheses and priors.", "Estimate likelihoods.", "Update.", "Compare expected outcomes and information value."),
        evidence_preferences=("Base rates", "calibrated forecasts", "diagnostic evidence"),
        failure_modes=("False precision", "laundering guesses through numbers", "ignoring model uncertainty"),
        blind_spots=("Dignity and rights", "unquantified structural change"),
        useful_when=("Choices depend on uncertain events", "new evidence can be acquired"),
        defer_when=("Inputs cannot be responsibly estimated", "rights constrain optimization"),
        sources=(
            _source("bayes-essay", "An Essay towards solving a Problem in the Doctrine of Chances", "Thomas Bayes", "Proposition 9 and scholium", "Updating probability from observed evidence"),
        ),
    ),
    Doctrine(
        id="consequentialist-analysis",
        name="Consequentialist Analysis",
        primary_question="Which option produces the strongest overall expected consequences?",
        primary_questions=("Who benefits and who is harmed?", "How likely and large are the effects?", "What second-order consequences matter?"),
        principles=("Count affected stakeholders impartially.", "Consider magnitude, probability, duration, and second-order effects.", "Make tradeoffs explicit."),
        procedure=("Enumerate stakeholders.", "Map benefits and harms.", "Weight likelihood and magnitude.", "Test distribution and second-order effects."),
        evidence_preferences=("Outcome data", "stakeholder impact evidence", "probability and magnitude estimates"),
        failure_modes=("Ignoring rights", "incommensurable values hidden in a score", "minority harms averaged away"),
        blind_spots=("Integrity of means", "uncertain long-tail effects"),
        useful_when=("Options have materially different stakeholder outcomes", "tradeoffs are unavoidable"),
        defer_when=("Rights or duties prohibit an option", "outcomes are too speculative to compare"),
        sources=(
            _source("mill-utilitarianism", "Utilitarianism", "John Stuart Mill", "Chapters II and V", "Consequences, qualitative goods, justice, and utility"),
        ),
    ),
)

_BY_ID = {doctrine.id: doctrine for doctrine in _DOCTRINES}


def list_doctrines() -> tuple[Doctrine, ...]:
    return _DOCTRINES


def get_doctrine(school_id: str) -> Doctrine:
    try:
        return _BY_ID[school_id]
    except KeyError as exc:
        choices = ", ".join(_BY_ID)
        raise KeyError(f"unknown school {school_id!r}; choose one of: {choices}") from exc


DEFAULT_COUNCIL = (
    "aristotelian-counsel",
    "stoic-counsel",
    "machiavellian-realism",
    "clausewitzian-strategy",
    "humean-skepticism",
)

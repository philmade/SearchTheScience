from enum import Enum


class PubMedFilterType(Enum):
    # Clinical Trials and Studies
    CLINICAL_TRIAL = "pubt.clinicaltrial"
    CLINICAL_TRIAL_PHASE_1 = "pubt.clinicaltrialphasei"
    CLINICAL_TRIAL_PHASE_2 = "pubt.clinicaltrialphaseii"
    CLINICAL_TRIAL_PHASE_3 = "pubt.clinicaltrialphaseiii"
    CLINICAL_TRIAL_PHASE_4 = "pubt.clinicaltrialphaseiv"
    OBSERVATIONAL_STUDY = "pubt.observationalstudy"
    RANDOMIZED_CONTROLLED_TRIAL = "pubt.randomizedcontrolledtrial"

    # High-Quality Evidence
    SYSTEMATIC_REVIEW = "pubt.systematicreview"
    META_ANALYSIS = "pubt.metaanalysis"

    # Other Study Types
    COMPARATIVE_STUDY = "pubt.comparativestudy"
    EVALUATION_STUDY = "pubt.evaluationstudy"
    VALIDATION_STUDY = "pubt.validationstudy"

    # Publication Types
    REVIEW = "pubt.review"
    GUIDELINE = "pubt.guideline"
    PRACTICE_GUIDELINE = "pubt.practiceguideline"
    CASE_REPORTS = "pubt.casereports"

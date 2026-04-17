Continues Assessment Type: Project Weight: 100%

Administrative Data:
This project is an individual Project assignment that is worth 100% of the final grade
awarded. 
Project overview
For the project, you are expected to perform the following tasks:
1. Identify and carry out a series of analytic tasks upon a large dataset of a specific
domain (or a collection of datasets that are somehow related or complement each
other).
2. Utilize appropriate tools and techniques for data extraction, processing, transformation, and analysis.
1
# Learning Outcome Description
LO1 Select, apply, and evaluate machine learning methodologies to facilitate preprocessing and transformation approaches.
LO2 Select, formulate, design, implement, and evaluate machine learning algorithms for
solving real-world problems using the latest industry practices and standards.
LO3 Contextualise, investigate, evaluate, and communicate key concepts and advanced
techniques for machine and deep learning algorithms.
LO4 Demonstrate expert knowledge of machine learning algorithms, tools, techniques
utilised in real world contexts.
3. Measure and compare the performance of ML and deep learning algorithms.
4. Summarize characteristics of the datasets using descriptive statistics.
5. Optionally, document your data collection process (if any).
You are required to produce an academic research paper-style report as well as the
implemented data analytics artefact. The assignment submission on the research project
is divided into two stages, namely Stage I and Stage II:
• Stage I: Develop a research proposal that includes a preliminary literature review.
In your proposal, clearly explain the background, context, and specific topic or hypothesis that you intend to explore. Your literature review should critically evaluate
key papers by examining their structure, content choices, argument development,
and language style. Reflect on how different authors approach the presentation and
discussion of their work.
Identify a research question or questions in machine learning that remain unaddressed in the current literature. Formulate a plan to investigate these questions,
detailing the data sources to be used, whether existing public datasets or newly
collected data. Outline your approach for data collection, measurement criteria,
relevant metrics, and how you intend to analyze the results to support your investigation. This plan should ensure a framework for repeatable and comprehensive
experiments.
• Stage II: You are required to develop a solution for the problem identified in
your preliminary investigation (Stage I), critically comparing the performance of
models/ methods on related datasets. Your models should be evaluated against existing state-of-the-art methods, which will serve as baselines. The
project’s main focus is to develop an ML-based solution that balances performance,
scalability, and latency/throughput.
Apply statistical analysis to understand data characteristics, and use multiple ML
techniques in your experiments. Employ appropriate evaluation tools to measure
model performance in terms of quality and latency, and conduct a thorough manual
error analysis for both your models and the baseline comparisons.
Note: Projects will be evaluated on novelty, technical quality, insightfulness, depth,
clarity, robustness, writing quality, and reproducibility. You must submit both code and
datasets, ensuring all algorithms and resources are clearly described for reproducibility,
including the experimental methodology, evaluations, and results. Reproducibility will
play a significant role in the assessment.
2
2 Key details, requirements, and definitions
Deliverables: There are deliverables for this project:
2. Final Report (PDF format)

Number of Methods: You are required to apply and critically evaluate at as mentioned in proposal.
Notions of Performance: Evaluating concepts/models in proposal

requires metrics tailored to both the specific task and model architecture. we need to use evaluation metrics from proposal or suitable as per problem solved in proposal
For example: regression
tasks, RMSE and MAE measure prediction accuracy, while for classification, Precision,
Recall, F1-score, and AUC-ROC are essential, particularly with imbalanced data. For
deep learning-specific evaluation, consider training dynamics (monitoring loss curves and
learning rate schedules), regularization metrics (validation loss and L2 penalties to control
overfitting), and task-specific metrics like IoU for computer vision and BLEU or perplexity for NLP models. Additionally, computational efficiency metrics, including training
time, inference latency, and model size, are crucial for deployment. Remember Selecting appropriate
metrics based on the problem and model type ensures a comprehensive understanding of
performance.
It is essential that the project shows unambiguous evidence of:
1. A critical analysis of fundamental methodologies to assess best
practice guidance when applied to computational problems (e.g. data mining, sentiment analysis, image captioning) in the specific context of the project.
2. The extraction, transformation, exploration, and cleaning of datasets in preparation
for building the methods used in the project;
3. The building and evaluation of models on a variety of datasets
and parameters; producing learning curve of your models on a varying sized
data sets, data domains and number of parameters.
4. Reporting performance (quality, latency and throughput) and scalability of the
models in varying-sized data sets
5. The extraction, interpretation, and evaluation of information and knowledge that
is drawn from the datasets used,
6. The critical review of relevant research to afford the assessment
of research methods applied in the project.

4 Final Report (80% Marks)
The final report must follow the IEEE conference format and should be between 7
double-column pages in length (this includes all figures, but not references or the project
cover sheet). For this report IEEE referencing style should be used. Papers over 7
pages will be subjected to a 5% point penalty, i.e., the maximum mark for the paper
will be 95%. Microsoft Word and LATEX templates are available at http://www.ieee.
org/conferences_events/conferences/publishing/templates.html. The following
structure is suggested for the final report:
1. Abstract: 100–150 words providing a high-level description of the project, its core
findings, and the domain of the datasets (not necessarily in this order).
2. Introduction: Provide an engaging introduction that motivates the work by
clearly explaining the context and importance of the project. State the research
4
questions or objectives, providing an overview of the problem being addressed. Optionally, offer a brief outline of the report structure, summarizing what each section
will cover (one to two sentences per section).
3. Literature Review: Conduct a detailed review of relevant literature, discussing
key works and techniques related to your project. Critically evaluate the strengths
and weaknesses of existing approaches and identify any research gaps that your
project aims to address. The literature review should establish the context for your
work and provide a foundation for your methodology.
Also, review any previous uses of the datasets and methods that are relevant. If
any established methods are being reused or adapted for your project, explain the
expected benefits and any potential modifications you plan to make.
4. Choice of methods: The choice of machine learning methods should be thoroughly justified, detailing why these specific models or algorithms are suitable for
addressing the research question. Discuss how the chosen methods align with the
data characteristics and overall project objectives, and highlight their strengths and
limitations. This section should clearly demonstrate how your selection of methods
effectively supports the goals of the project.
5. Methodology: Describe in detail the approach taken to address the research questions or objectives. Outline the key steps followed, including data collection,
preprocessing, and transformation phases. Provide a detailed explanation of
any technical elements involved, such as data cleaning, feature engineering,
model selection, or experimental design. If you have used any dimensionality reduction (e.g PCA, LDA) or any feature selection (forward/backward, RFE,
etc.) techniques , that should also be discussed here. This section should provide
sufficient clarity to enable the replication of your approach.
6. Evaluation: Detail the evaluation methodology used to validate your approach,
including how you assessed performance and why the chosen metrics are appropriate. Explain how parameters were tuned, the rationale behind these choices, and
their potential impact on model performance. Provide a comprehensive analysis of
your findings, discussing the implications, strengths, weaknesses, and any insights
or challenges in interpreting the results.
Include a subsection Error Analysis to discuss the errors encountered during
model evaluation. You should also discuss any reasons for underperformance, biases,
or limitations in the dataset or model design. Evaluate how different parameters,
regularization, and optimizations used throughout the project have impacted the
results. Reflect on any remaining issues and suggest possible ways to refine or
improve the models.(include figures)
7. Conclusions and Future Work: Summarize the key findings of your research
and their implications. Discuss any limitations encountered in the study and propose potential extensions or improvements for future work. Reflect on how your
research contributes to the field and offers partial answers to the research questions
or objectives, emphasizing the broader significance of your results and the possible
next steps for further investigation.
5
8. References: Include a list of references used in your report. Note that websites
are not references; they should be referred to in footnotes.
Although not recommended, you may remove, change and/or alter methods, datasets
and/or key research question(s) or objective(s) after submission of the Proposal / Interim
Progress Report.

Table 2: Grading Rubric for Proposal (20%)
Criteria H1 (>70%) H2 (50–69%) Pass (40–59%)
Motivation &
Background
(10%)
Provides a well-justified and thorough background of the problem, with clear motivation for using ML/DL techniques. Demonstrates excellent understanding of
the context.
Provides sufficient background
with some motivation for using model/techniques. Demonstrates a reasonable understanding of the context, though may
lack depth.
Lacks clear motivation or background; insufficient reasoning for
using techniques. Limited understanding of the context.
Research Question (15%) Clearly articulated, specific, and measurable research question(s)
or hypothesis, well-aligned with
the project objectives.
Reasonably clear research question(s) or hypothesis, though may
lack specificity or full alignment
with project objectives.
Vague or overly broad research
question(s) that lack clarity and
alignment with the project objectives.
Initial Review of
Literature (20%)
Comprehensive and critical review of at least 5–7 relevant papers, identifying research gaps effectively. Demonstrates strong
integration and understanding of
literature.
Adequate review of relevant literature, with some evaluation of 5–
7 papers. However, critical analysis or depth may be limited. Some
gaps in understanding.
Limited or superficial review of
literature; fewer than 5 papers
reviewed, lacking critical evaluation. Little integration or understanding of context.
Data Sources &
Statistics (15%)
Clearly identifies potential
datasets with a thorough description (e.g., format, size, statistics).
Discusses the data’s suitability
for the problem effectively.
Identifies relevant datasets with
some description. Discussion on
suitability is present but may lack
detail or strong connection to the
project.
Insufficient identification or description of datasets. Lacks
meaningful discussion of suitability for the problem.
7
Criteria H1 (>70%) H2 (50–69%) Pass (40–59%)
Methods (ML &
DL Techniques
(20%)
Provides a detailed overview of
the chosen ML and DL techniques, including at least two
ML models and one deep learning models. Strong rationale for
selection, linked to the research
question.
Describes chosen ML and DL
techniques with basic rationale.
Connection to the research question is present but may not be
strong or fully justified.
Inadequate overview of methods or insufficient justification for
their selection. Limited connection to the research question.
Evaluation
Methods (10%)
Clearly outlines the evaluation
strategy, including relevant metrics (e.g., accuracy, RMSE, F1-
score), with strong rationale for
their selection.
Provides an outline of evaluation
methods and identifies metrics,
though the rationale may not be
clear or fully aligned with the
problem.
Inadequate or unclear evaluation
plan; lacks relevant performance
metrics or fails to provide an explanation for their selection.
Clarity & Presentation (10%) Well-organized and clearly writ- ten; adheres strictly to the IEEE
format. Free of grammatical errors and easy to follow.
Adequately written and organized; minor issues with formatting or clarity. Contains some
grammatical errors.
Poorly written or disorganized;
does not adhere to the IEEE format effectively. Contains several
grammatical errors.
8
Table 3: Grading Rubric for Project (80%)
Criteria H1 (>70%) H2.1 (60–69%) H2.2 (50–59%) Pass (40–49%) Fail (< 40%)
Objectives and
Motivation
(10%)
Objectives are
challenging, wellpresented, and
fully met, with
strong motivation
and discussion
that effectively
ties them to the
context.
Appropriate
project objectives
are clearly stated,
mostly met, and
well-motivated.
The discussion ties
them effectively to
the project.
Objectives are
stated, mostly met,
and reasonably
motivated, though
with some minor
gaps in clarity or
connection to the
project.
Clear objectives
are present and
partially met, with
limited motivation
and weaker ties
to the research
context.
Objectives are unclear, poorly presented, or not met.
Little to no motivation or relevant discussion provided.
Discussion and
Related Work
(10%)
Very good discussion of related work
with a clear evaluation of strengths
and limitations.
Paper choices effectively situate the
project within the
literature.
Good discussion
and evaluation
of related work.
Chosen papers
are relevant and
contribute to the
context of the
project.
Appropriate discussion of related
work, but evaluation may lack
depth. Paper
choices generally relate to the
project but could
be more targeted.
Discussion of
related work is
present but lacks
detail or depth.
The choice of
papers provides
limited context for
the project.
Limited or inadequate discussion of
related work, or
papers chosen are
irrelevant or arbitrarily selected.
Choice of Methods (10%) A well-considered selection of some
complex methods,
demonstrating a
thoughtful approach to the
research objectives.
Application of
at least two advanced methods
that are suitable
for addressing the
project objectives.
Application of at
least one advanced
method that is
mostly appropriate
for the research
objectives.
Methods are appropriate but may be
standard or lacking in complexity.
Choices appear safe
rather than innovative.
Methods chosen
are arbitrary,
poorly justified, or
not well-aligned
with the research
objectives.
9
Criteria H1 (>70%) H2.1 (60–69%) H2.2 (50–59%) Pass (40–49%) Fail (< 40%)
Methodology
(25%)
Thorough application of
KDD/CRISPDM methodologies,
with minor errors
or shortcuts that
are generally well
justified.
All stages of
KDD/CRISP-DM
are appropriately
applied, though
some depth may
be lacking or minor
errors present.
Stages of
KDD/CRISPDM are mostly
applied, but there
is a lack of depth
or significant errors
in the approach.
KDD/CRISP-DM
stages are inconsistently applied,
with noticeable
gaps in methodology or lack of
justification.
Poor or unclear
application of
KDD/CRISP-DM
methodologies.
Significant gaps or
incorrect application.
Evaluation
(20%)
All key decisions
are justified with
literature. The
project goes beyond simple model
application, exploring different
scenarios and parameterizations
to provide a rich
understanding of
performance.
Most key decisions
are justified with
literature, and
the project extends beyond basic
model application,
attempting to
investigate different scenarios and
parameterizations.
Key decisions are
justified, but with
limited depth. The
project attempts
to go beyond basic
model application,
but with partial
success.
Key decisions are
somewhat justified
with limited depth.
The project lacks
significant differentiation in evaluation.
Decisions lack justification or connection to literature. Evaluation is
superficial or lacks
depth.
10
Criteria H1 (>70%) H2.1 (60–69%) H2.2 (50–59%) Pass (40–49%) Fail (< 40%)
Conclusion and
Future Work
(10%)
Strong conclusions
that grasp limitations and implications, anchored
with relevant literature. Future work
is thoughtful and
well-connected to
the project.
Conclusions show
understanding of
implications and
limitations, with
some relevant literature support.
Future work is
appropriate, but
lacks creativity.
Conclusions are appropriate but may
lack depth. Future work is discussed but lacks innovation or strong
connection to the
project.
Conclusions are
weak, with little
insight into limitations. Future
work is minimally discussed or
arbitrary.
Conclusions are absent or unclear. No
meaningful discussion of limitations
or future work.
Presentation and
Quality (10%)
Well-written report with very
few language or
formatting errors.
Adheres well to
the IEEE template, with mostly
clear and relevant
figures.
Readable report
with some minor
language or style
issues. Largely
adheres to the
IEEE template,
with most figures
presented well.
Readable, though
with several language or style errors. Adheres to
the IEEE template,
though figures may
lack clarity or relevance.
Noticeable language errors and
poor adherence
to formatting.
Figures may be unclear or improperly
formatted.
Report is poorly
written with significant language issues, and figures
are unclear or not
aligned with the
IEEE template.
Video Presentation (5%) Well-structured video effectively
demonstrating key
functionalities and
methods, with
good commentary on project
implications and
limitations.
Clear and appropriate video covering main functionalities and methodologies, with some
relevant discussion
on results and limitations.
A video is provided that covers
essential functionalities and methods, though commentary may lack
detail.
A video is provided
but lacks depth
in demonstrating
key methods or
di
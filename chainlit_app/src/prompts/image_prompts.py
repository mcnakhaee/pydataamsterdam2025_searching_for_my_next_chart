IMAGE_PROMPT = f"""
You are an expert in data visualization with deep knowledge of typography, color theory, and visualization design patterns inspired by ggplot2 concepts.

You will be provided with an image of a data visualization.
Your task is to analyze the visualization and produce a structured output.

General Output Formatting Rules
Follow the section order exactly as listed below — do not add or rename sections.

Each section name must appear exactly as written (e.g., Section_1_Plot_Type).

Separate sections using %%%.

Separate multiple values within a section using *.

For typography, output each element in this format:
Element|font_family|font_type|font_size|alignment|style|color
Example: Title|Arial|Sans-serif|24px|center|bold|darkgrey.

If a feature is not present, write "Not implemented" (do not use "Not specified").

Always produce the same field order within each section.

Ensure the output can be parsed line-by-line into a table.

Sections to Output
Section_1_Plot_Type
Primary_Category → exactly 1

Subcategory → one or more

Specific_Variant_Technique → one or more

Section_2_Data_and_Variable_Types
List variables and classify each using:

Continuous, Discrete, Categorical, Ordinal, Temporal

Geolocation, Geometric Shapes, Topology

Graph Structures, Hierarchical

Strings, Tokens, Semantic Embeddings

Binary Values, Flags

Mixed Types, Multivariate Records, Lists/Sets

Probability Distributions, Fuzzy Values

Image, Audio, Video

Section_3_Variable_Mapping
Format: Variable_Name: Encoding
Example: Methamphetamine concentration: color * Population size: circle area

Section_4_Color_Encoding
Palette_Type

Gradient_Type_Direction_Midpoints

Key_Colors (Named + HEX/RGB)

Number_of_Distinct_Colors

Grid_Color (Named + HEX/RGB)

Contrast_Assessment

Accessibility_Assessment

Semantic_Meaning

Section_5_Theme
Background_Color (Named + HEX/RGB)

Text_Colors (Title, Subtitle, Annotations)

Background_Type (Light/Dark)

Grid_Orientation (Horizontal, Vertical, Both, None)

Grid_Layout (Regular, Logarithmic, Polar, Faceted)

Grid_Type (Major, Minor, Custom)

Grid_Style (Solid, Dashed, Light, Colored)

Grid_Special_Variants (Heatmap, Lattice, Custom Shapes, Annotation Bands)

Section_6_Legend_and_Guide_Details
Position

Orientation

Color_Legend_Type (Continuous/Discrete)

Legend_Title

Symbol_Size_and_Spacing

Background_and_Border

Color_Bar_Configuration

Guide_Annotations

Legend_Modifications

Section_7_Chart_Element_Identification
Reference_Aids (Lines, Bands, Regions)

Statistical_Summaries (Mean, Median, Quartiles, Confidence Intervals, Regression)

Highlighting (Color, Opacity, Shape/Size)

Section_8_Grid_Arrangement
Arrangement_Type (Rows, Columns, Facets, Irregular, Polar, Small Multiples, Trellis, Adaptive)

Section_9_Layout
Structure_Description

Aspect_Ratio

Proportions_and_Dimensions

Section_10_Axes_and_Scales
For each axis:

Scale_Type

Position

Tick_Frequency_and_Style

Visible_Range_and_Transformations

Grid_Lines (Major/Minor/None)

Axis_Breaks

Aspect_Ratio

Secondary_or_Dual_Scales

Section_11_Coordinate_Systems
Coordinate_Type (Cartesian, Polar, Map Projection, Ternary, Parallel, Network, 3D, Custom)

Section_12_Typography
Format:
Element|font_family|font_type|font_size|alignment|style
Include entries for:

Title

Subtitle

Caption

Axis_Labels

Legend_Text

Annotation_Text

Section_13_Statistical_Analytical_Methods_Used
Data_Smoothing_Methods

Statistical_Models

Aggregation_Methods

Binning_Strategy

Normalization_or_Scaling

Section_14_Annotation_and_Storytelling_Elements
Callouts_or_Leader_Lines

Inline_Explanations

Numbered_Steps

Contextual_References

Section_15_Plot_Goal
Observed_Patterns

Applications (4–6 specific uses)

Section_16_Data_Source
Source_Name

Year

Section_17_Searchable_Keywords
Provide 10–15 keywords:

Visualization techniques

Style elements

Data domains

Geographic focus

Color schemes

Implementation methods

Section_18_Best_Practices
Readability_Assessment

Data_Ink_Ratio

Color_Accessibility_Assessment

Section_19_Innovative_or_Noteworthy_Design_Features
Identify and extract interesting, clever, or innovative design elements used in the visualization. These may include:

Unusual combinations of visual encodings (e.g., using both size and color for different variables)

Smart layout choices, grid arrangements, or use of space

Design decisions that enhance readability, clarity, or accessibility

Subtle elements that guide attention, such as selective labeling, desaturation, contrast, or annotations

Use of uncommon chart types, coordinate systems, or hybrid visuals

Any thoughtful stylistic choices that elevate the effectiveness of the visualization

Output Requirements:

List 3 to 5 concise bullet points, each describing a unique or thoughtful design choice

Use specific visual vocabulary (e.g., “proportional symbol encoding,” “highlighting via color saturation,” “label clustering avoidance”)

Do not interpret the underlying data — focus only on visual design and structural techniques

Emphasize what makes each element noteworthy or clever, not just that it exists


section_11_description
Generate a 5-sentence summary that:

Identifies the plot type (including primary category, subcategory, and specific variant/technique) and the coordinate system used.

Lists the variables represented, their data types, and how each variable is visually encoded (position, size, color, shape, angle, etc.).

Describes the visual structure — layout, grid arrangement, axes/scales, legend configuration, and typography hierarchy.

Details color usage — palette type, gradient or discrete scheme, number of distinct colors, and any notable accessibility considerations.

Mentions additional design elements such as annotations, highlighting techniques, interactivity (if applicable), and special stylistic choices that affect readability.

Output Requirements:

Avoid interpreting the underlying data or explaining patterns in the dataset — focus solely on how the visualization is constructed.

Use precise technical vocabulary so the description is searchable in a RAG system (e.g., “polar coordinate system,” “faceted grid layout,” “sequential diverging palette,” “categorical axis”).

Ensure the summary can stand alone as a feature-level description of the visualization without needing to reference the dataset’s meaning.

"""
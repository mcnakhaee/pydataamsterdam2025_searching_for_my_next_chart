import re
import pandas as pd
from typing import List, Dict

SECTION_ORDER = [
    "Section_1_Plot_Type",
    "Section_2_Data_and_Variable_Types",
    "Section_3_Variable_Mapping",
    "Section_4_Color_Encoding",
    "Section_5_Theme",
    "Section_6_Legend_and_Guide_Details",
    "Section_7_Chart_Element_Identification",
    "Section_8_Grid_Arrangement",
    "Section_9_Layout",
    "Section_10_Axes_and_Scales",
    "Section_11_Coordinate_Systems",
    "Section_12_Typography",
    "Section_13_Statistical_Analytical_Methods_Used",
    "Section_14_Annotation_and_Storytelling_Elements",
    "Section_15_Plot_Goal",
    "Section_16_Data_Source",
    "Section_17_Searchable_Keywords",
    "Section_18_Best_Practices",
    "Section_19_Description",
]

def parse_llm_visualization_output(text: str) -> Dict[str, any]:
    """
    Parse the structured LLM output into a flat dictionary suitable for DataFrame ingestion.
    """
    # Split into sections
    raw_sections = re.split(r"%%%+", text)
    parsed: Dict[str, any] = {}
    
    # Helper to clean and split values
    def split_vals(val_str):
        parts = [v.strip() for v in val_str.split('*') if v.strip()]
        return parts if parts else ["Not implemented"]
    
    for raw in raw_sections:
        raw = raw.strip()
        if not raw:
            continue
        # Expect section header like "Section_1_Plot_Type"
        first_line, *rest = raw.splitlines()
        header_match = re.match(r"(Section_[0-9]+_[A-Za-z0-9_]+)", first_line.strip())
        if not header_match:
            continue
        section_name = header_match.group(1)
        body = "\n".join(rest).strip()
        if section_name == "Section_1_Plot_Type":
            # Primary, Subcategory, Specific
            # Example line: Primary Category: Spatial & Geospatial * Subcategory: Maps * ...
            # We'll capture key: value parts separated by '*'
            entries = split_vals(body)
            for entry in entries:
                if ':' in entry:
                    key, val = entry.split(':', 1)
                    parsed[f"{section_name}__{key.strip().replace(' ', '_')}"] = val.strip()
                else:
                    parsed[f"{section_name}__unknown"] = entry
        elif section_name == "Section_2_Data_and_Variable_Types":
            # Expect variable definitions like "Variable 1: Meth concentration → Continuous"
            lines = [l.strip() for l in body.split('*') if l.strip()]
            vlist = {}
            for line in lines:
                # e.g., "Variable 1: Methamphetamine concentration in mg per 1000 inhabitants → Continuous"
                if ':' in line:
                    var_part, type_part = line.split('→') if '→' in line else (line, "")
                    var_name = var_part.split(':', 1)[1].strip() if ':' in var_part else var_part.strip()
                    types = [t.strip() for t in type_part.split(',') if t.strip()]
                    vlist[var_name] = types or ["Not implemented"]
            parsed[section_name] = vlist
        elif section_name == "Section_3_Variable_Mapping":
            # e.g., "Methamphetamine concentration: color * Population size: circle area"
            entries = split_vals(body)
            mapping = {}
            for entry in entries:
                if ':' in entry:
                    var, enc = entry.split(':', 1)
                    mapping[var.strip()] = enc.strip()
            parsed[section_name] = mapping
        elif section_name == "Section_12_Typography":
            # Each entry like Title|Arial|Sans-serif|24px|center|bold
            lines = [l.strip() for l in body.split('*') if l.strip()]
            typo = {}
            for line in lines:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 6:
                    element = parts[0]
                    typo[element] = {
                        "font_family": parts[1],
                        "font_type": parts[2],
                        "font_size": parts[3],
                        "alignment": parts[4],
                        "style": parts[5],
                    }
            parsed[section_name] = typo
        elif section_name in ("Section_17_Searchable_Keywords", "Section_19_Description"):
            # Keywords: split by * or comma
            if '*' in body:
                parsed[section_name] = split_vals(body)
            else:
                parsed[section_name] = [k.strip() for k in re.split(r"[,@;]+", body) if k.strip()]
        elif section_name == "Section_16_Data_Source":
            # Expect Source_Name and Year; crude split
            parts = split_vals(body)
            parsed[section_name] = parts
        else:
            # Generic key: value split by '*' and ':' 
            entries = split_vals(body)
            for entry in entries:
                if ':' in entry:
                    key, val = entry.split(':', 1)
                    parsed[f"{section_name}__{key.strip().replace(' ', '_')}"] = val.strip()
                else:
                    parsed[f"{section_name}__extra"] = entry

    return parsed

def build_dataframe_from_outputs(outputs: List[str]) -> pd.DataFrame:
    """
    Given a list of raw LLM output strings, parse each and build a DataFrame.
    """
    records = []
    for o in outputs:
        record = parse_llm_visualization_output(o)
        records.append(record)
    df = pd.DataFrame.from_records(records)
    return df

# Example usage with a single earlier output string:
if __name__ == "__main__":
    sample_output = """
%%% Section_1_Plot_Type %%%
Primary Category: Spatial & Geospatial * Subcategory: Maps * Proportional Symbol Maps * Specific Variant / Technique: Choropleth overlay with proportional circles * Annotated map
%%% Section_2_Data_and_Variable_Types %%%
Variable 1: Methamphetamine concentration in mg per 1000 inhabitants → Continuous * Variable 2: City location → Geolocation * Variable 3: Population size → Continuous (circle area encoding) * Variable 4: Country names → Categorical
%%% Section_3_Variable_Mapping %%%
Methamphetamine concentration: color * Population size: circle area * City location: latitude/longitude position * Country: implicit via map base layer
%%% Section_4_Color_Encoding %%%
Palette type: Sequential * Gradient: vertical legend from light blue (~#5FA8D3) through orange (~#F4A261) to deep red (~#9B2226) * Key colors: light blue (#5FA8D3), orange (#F4A261), deep red (#9B2226), black (#000000) for highest concentration city * Distinct colors: ~6 gradient steps * Grid colors: Not implemented * Contrast: high between colored points and pale background * Accessibility: sequential gradient may be partially challenging for red–green deficiencies but largely distinguishable due to saturation difference * Semantic meaning: red = higher methamphetamine concentration, blue = lower concentration
%%% Section_5_Theme %%%
Background: light grey (#EAE6E1) * Title/subtitle text: black (#000000) * Annotations text: black (#000000) * Background type: light * Grids: Not implemented (map background instead)
%%% Section_6_Legend_and_Guide_Details %%%
Legend position: top left * Legend orientation: vertical * Color legend: continuous gradient * Legend title: “Meth in mg per 1000 inhabitants” * Legend symbols: gradient bar for color, circles for population sizes * Legend background: none (transparent over map) * Color bar: gradient from blue → orange → red * Additional guides: circle size legend labeled as population
%%% Section_7_Chart_Element_Identification %%%
Reference Aids: map outline * Statistical Summaries: not implemented * Highlighting: black circle around Ústí nad Labem (highest value) * bold annotation labels for key cities
%%% Section_8_Grid_Arrangement %%%
Irregular/free-form layout (map projection with scattered points)
%%% Section_9_Layout %%%
Single main map filling frame * Portrait aspect ratio * Centered content with legend inset at top left
%%% Section_10_Axes_and_Scales %%%
Axes: Not implemented (geographic projection without visible axes) * Scale: geographic coordinate scaling via map projection
%%% Section_11_Coordinate_Systems %%%
Geographic projection: Planar (likely equal-area or similar) * Unprojected lat/long visually transformed to Europe map projection
%%% Section_12_Typography %%%
Title|Unknown|Sans-serif|Large|center|bold * Subtitle|Unknown|Sans-serif|Medium|left|normal * Annotation|Unknown|Sans-serif|Small|near-point|normal
%%% Section_13_Statistical_Analytical_Methods_Used %%%
Not implemented
%%% Section_14_Annotation_and_Storytelling_Elements %%%
Callouts_or_Leader_Lines: yes * Inline_Explanations: city labels with lines * Numbered_Steps: Not implemented * Contextual_References: Ústí nad Labem labeled as highest concentration
%%% Section_15_Plot_Goal %%%
Patterns: Czech cities show high methamphetamine concentration; Ústí nad Labem highest in Europe; many Western/Northern European cities lower * Applications: drug policy monitoring * wastewater epidemiology * public health awareness * regional law enforcement resource allocation * academic studies in substance abuse epidemiology
%%% Section_16_Data_Source %%%
SCORE Network (2024)
%%% Section_17_Searchable_Keywords %%%
methamphetamine * wastewater analysis * European drug trends * proportional symbol map * sequential color scale * population circles * public health visualization * drug policy data * geographic mapping * color gradient legend * data journalism * annotated cities * geospatial analysis * SCORE Network * drug concentration mapping
%%% Section_18_Best_Practices %%%
Readability: good * Data–ink ratio: efficient (minimal extra decoration) * Color accessibility: reasonable but sequential palette could be optimized for red–green deficiencies
%%% Section_19_Description %%%
This visualization is a proportional symbol map of Europe showing daily average methamphetamine concentration in wastewater by city. Colors range from blue (low) to deep red (high), with the largest concentration observed in Ústí nad Labem, Czech Republic. Circle sizes represent city population, providing a secondary layer of context. A clear, minimalistic design with a pale background ensures strong contrast for the colored points. The map effectively communicates spatial patterns in drug usage, highlighting both regional trends and extreme outliers.
"""
    df = build_dataframe_from_outputs([sample_output])
    print(df.T)  # transpose to inspect fields
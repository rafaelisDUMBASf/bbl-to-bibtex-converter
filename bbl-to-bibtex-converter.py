"""
BBL to BibTeX Converter

A Python script to convert LaTeX bibliography files (.bbl) to BibTeX format (.bib).
"""

import re
import sys
import argparse


def convert_bibitem_to_bibtex(bibitem):
    """
    Convert a single bibitem entry to BibTeX format.
    
    Args:
        bibitem (str): A single \bibitem entry from a .bbl file
        
    Returns:
        str: BibTeX formatted entry, or None if conversion fails
    """
    try:
        # Extract citation key - pattern: \bibitem[...]{key}
        key_match = re.search(r'\\bibitem(?:\[[^\]]+\])?\{([^}]+)\}', bibitem)
        if not key_match:
            return None
        key = key_match.group(1).strip()
        
        # Extract authors - text between \bibitem{key} and first \newblock
        author_match = re.search(r'\\bibitem(?:\[[^\]]+\])?\{[^}]+\}\s*(.+?)(?=\\newblock)', bibitem, re.DOTALL)
        if not author_match:
            return None
        authors = author_match.group(1).strip()
        # Clean up authors: remove extra whitespace, handle line breaks, remove trailing period
        authors = re.sub(r'\s+', ' ', authors)
        authors = authors.rstrip('.')
        # Split by comma and join with ' and ', handling cases where 'and' already exists
        author_list = []
        for a in authors.split(','):
            a = a.strip().rstrip('.')
            if a:
                # Remove leading 'and' if present (will be added back when joining)
                a = re.sub(r'^\s*and\s+', '', a, flags=re.IGNORECASE)
                author_list.append(a)
        authors = ' and '.join(author_list)

        # Extract title - first \newblock content
        title_match = re.search(r'\\newblock\s+(.+?)(?=\\newblock|\\emph|$)', bibitem, re.DOTALL)
        if not title_match:
            return None
        title = title_match.group(1).strip()
        # Clean up title: remove extra whitespace and line breaks
        title = re.sub(r'\s+', ' ', title)

        # Extract other fields
        fields = {}
        
        # Determine entry type first (needed for field naming)
        is_conference = re.search(r'In\s+\\emph\{', bibitem) is not None
        
        # Extract journal/venue - in \emph{...}
        journal_match = re.search(r'\\emph\{([^}]+)\}', bibitem, re.DOTALL)
        if journal_match:
            journal = journal_match.group(1).strip()
            journal = re.sub(r'\s+', ' ', journal)
            # Use 'booktitle' for conferences, 'journal' for articles
            if is_conference:
                fields['booktitle'] = journal
            else:
                fields['journal'] = journal

        # Extract year - pattern: , YYYY. or YYYY.
        year_match = re.search(r',\s*(\d{4})\.', bibitem)
        if not year_match:
            # Try alternative pattern without comma
            year_match = re.search(r'\b(\d{4})\.', bibitem)
        if year_match:
            fields['year'] = year_match.group(1).strip()

        # Extract URL
        url_match = re.search(r'URL\s+\\url\{([^}]+)\}', bibitem, re.DOTALL)
        if url_match:
            fields['url'] = url_match.group(1).strip()

        # Determine entry type
        if is_conference:
            entry_type = 'inproceedings'
        elif 'journal' in fields or 'arXiv' in fields.get('journal', '').lower():
            entry_type = 'article'
        else:
            entry_type = 'article'  # default

        # Build bibtex entry
        bibtex_entry = f"@{entry_type}{{{key},\n"
        bibtex_entry += f"  author = {{{authors}}},\n"
        bibtex_entry += f"  title = {{{title}}},\n"
        for field, value in fields.items():
            bibtex_entry += f"  {field} = {{{value}}},\n"
        bibtex_entry = bibtex_entry.rstrip(',\n') + '\n'  # Remove trailing comma
        bibtex_entry += "}\n"

        return bibtex_entry
    except Exception as e:
        print(f"Error processing bibitem: {e}", file=sys.stderr)
        return None


def process_all_bibitems(bbl_content):
    """
    Process all bibitems in a .bbl file and convert them to BibTeX format.
    
    Args:
        bbl_content (str): Content of the .bbl file
        
    Returns:
        str: Combined BibTeX content with all entries
    """
    bibtex_entries = []

    # Split the bbl content into individual bibitems
    bibitems = re.split(r'\n(?=\\bibitem)', bbl_content)

    for item in bibitems:
        bibtex_entry = convert_bibitem_to_bibtex(item)
        if bibtex_entry:
            bibtex_entries.append(bibtex_entry)

    # Combine all valid bibtex entries into a single string
    bibtex_content = '\n\n'.join(bibtex_entries)

    return bibtex_content


def main(bbl_file_path, bibtex_file_path):
    """
    Main function to convert a .bbl file to .bib format.
    
    Args:
        bbl_file_path (str): Path to the input .bbl file
        bibtex_file_path (str): Path to the output .bib file
    """
    try:
        # Read the .bbl file
        with open(bbl_file_path, 'r', encoding='utf-8') as file:
            bbl_content = file.read()

        # Process all bibitems and generate the bibtex content
        bibtex_content = process_all_bibitems(bbl_content)

        # Write the valid bibtex content to a .bib file
        with open(bibtex_file_path, 'w', encoding='utf-8') as file:
            file.write(bibtex_content)
        
        print(f"Conversion complete! Output written to {bibtex_file_path}")
        return 0
    except FileNotFoundError:
        print(f"Error: Input file '{bbl_file_path}' not found.", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def parse_arguments():
    """
    Parse command-line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='Convert LaTeX bibliography files (.bbl) to BibTeX format (.bib)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.bbl output.bib
  %(prog)s -i example.bbl -o example_output.bib
  %(prog)s example.bbl  # Output will be example.bib
        """
    )
    
    parser.add_argument(
        'input',
        nargs='?',
        help='Input .bbl file path'
    )
    
    parser.add_argument(
        'output',
        nargs='?',
        help='Output .bib file path (optional, defaults to input filename with .bib extension)'
    )
    
    parser.add_argument(
        '-i', '--input',
        dest='input_file',
        metavar='FILE',
        help='Input .bbl file path (alternative to positional argument)'
    )
    
    parser.add_argument(
        '-o', '--output',
        dest='output_file',
        metavar='FILE',
        help='Output .bib file path (alternative to positional argument)'
    )
    
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    
    # Determine input file (prefer -i/--input flag, then positional argument)
    if args.input_file:
        bbl_file_path = args.input_file
    elif args.input:
        bbl_file_path = args.input
    else:
        print("Error: Input file is required.", file=sys.stderr)
        print("Usage: python bbl-to-bibtex-converter.py <input.bbl> [output.bib]", file=sys.stderr)
        print("   or: python bbl-to-bibtex-converter.py -i <input.bbl> [-o <output.bib>]", file=sys.stderr)
        sys.exit(1)
    
    # Determine output file (prefer -o/--output flag, then positional argument, then default)
    if args.output_file:
        bibtex_file_path = args.output_file
    elif args.output:
        bibtex_file_path = args.output
    else:
        # Default: replace .bbl extension with .bib
        if bbl_file_path.endswith('.bbl'):
            bibtex_file_path = bbl_file_path[:-4] + '.bib'
        else:
            bibtex_file_path = bbl_file_path + '.bib'
    
    exit_code = main(bbl_file_path, bibtex_file_path)
    sys.exit(exit_code)


"""
BBL to BibTeX Converter

A Python script to convert LaTeX bibliography files (.bbl) to BibTeX format (.bib).
"""

import re


def convert_bibitem_to_bibtex(bibitem):
    """
    Convert a single bibitem entry to BibTeX format.
    
    Args:
        bibitem (str): A single \bibitem entry from a .bbl file
        
    Returns:
        str: BibTeX formatted entry, or None if conversion fails
    """
    try:
        # Extract citation key
        key_match = re.search(r'\{([^,]+),', bibitem)
        if not key_match:
            return None
        key = key_match.group(1)
        
        # Extract authors
        author_match = re.search(r'\bibitem\[[^\]]+\]\{([^}]+)\}(.+?)(?=\\newblock)', bibitem, re.DOTALL)
        if not author_match:
            return None
        authors = author_match.group(2).strip()
        authors = ' and '.join([a.strip() for a in authors.split(',')])

        # Extract title
        title_match = re.search(r'\\newblock\s+(.+?)(?=\\newblock|\\emph)', bibitem, re.DOTALL)
        if not title_match:
            return None
        title = title_match.group(1).strip()

        # Extract other fields
        fields = {}
        journal_match = re.search(r'\\emph\{(.+?)\}', bibitem, re.DOTALL)
        if journal_match:
            fields['journal'] = journal_match.group(1).strip()

        year_match = re.search(r',\s+(\d{4})\.', bibitem)
        if year_match:
            fields['year'] = year_match.group(1).strip()

        url_match = re.search(r'URL\s+\\url\{(.+?)\}', bibitem)
        if url_match:
            fields['url'] = url_match.group(1).strip()

        # Build bibtex entry
        entry_type = 'article' if 'journal' in fields else 'inproceedings'
        bibtex_entry = f"@{entry_type}{{{key},\n"
        bibtex_entry += f"  author = {{{authors}}},\n"
        bibtex_entry += f"  title = {{{title}}},\n"
        for field, value in fields.items():
            bibtex_entry += f"  {field} = {{{value}}},\n"
        bibtex_entry = bibtex_entry.rstrip(',\n') + '\n'  # Remove trailing comma
        bibtex_entry += "}\n"

        return bibtex_entry
    except Exception as e:
        print(f"Error processing bibitem: {bibitem}\n{e}")
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
    # Read the .bbl file
    with open(bbl_file_path, 'r', encoding='utf-8') as file:
        bbl_content = file.read()

    # Process all bibitems and generate the bibtex content
    bibtex_content = process_all_bibitems(bbl_content)

    # Write the valid bibtex content to a .bib file
    with open(bibtex_file_path, 'w', encoding='utf-8') as file:
        file.write(bibtex_content)
    
    print(f"Conversion complete! Output written to {bibtex_file_path}")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) == 3:
        bbl_file_path = sys.argv[1]
        bibtex_file_path = sys.argv[2]
        main(bbl_file_path, bibtex_file_path)
    else:
        print("Usage: python convert_bbl_to_bibtex.py <input.bbl> <output.bib>")
        print("Example: python convert_bbl_to_bibtex.py main.bbl main.bib")


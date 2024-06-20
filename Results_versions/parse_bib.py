from bibtexparser import *



####################################### INPUTS #######################################



entry_key_to_check = "series"
checked_values = ["CHI EA", "CHI PLAY", "UIST ", "ISMAR "] # The space is important to avoid matching "CHIIR" for example
next_file_name = "Victor" # 2 digits
mode = "w" # "w" to overwrite the file, "a" to append to the file

do_write = True # Set to True to write the new file



######################################################################################



file_name = "c:/Users/nlufulua/Documents/code/ACM-Research/Results_versions/ACM/acm_requete1.bib"
bib_database:Library = parse_file(file_name)

# On récupère les données des articles de la conférence CHI
blocks_to_keep = []
for i, entry in enumerate(bib_database.entries):
    try:
        for checked_value in checked_values:
            ok = entry[entry_key_to_check].startswith(checked_value)
            if ok:
                print(entry_key_to_check + " = {" + entry[entry_key_to_check] + "}")
                blocks_to_keep.append(bib_database.blocks[i])
                break
    except KeyError:
        continue

while len(bib_database.blocks) > 0:
    bib_database.blocks.pop()

for block in blocks_to_keep:
    bib_database.blocks.append(block)

print(f"Kept {len(blocks_to_keep)} entries")

new_file = f"c:/Users/nlufulua/Documents/code/ACM-Research/Results_versions/{next_file_name}.bib"
with open(new_file, mode, encoding='utf-8') as f:
    if do_write:
        bibtexparser.write_file(f, bib_database)
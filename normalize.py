import yaml
import re

policyname = input("Enter the name of the file to read.\n")
file_out_name = policyname.split('.')[0] + ".yml"
print(file_out_name)

policy = open(policyname, "r", encoding = "utf8")
policytext = policy.readlines()

# remove lines that are just whitespace
policytext[:] = [line for line in policytext if not (line == '\n')]
for i in range (0, len(policytext)):
    # remove non-ASCII characters
    policytext[i] = re.sub("[^\x00-\x7F]+", "", policytext[i])
    # remove excess whitespace
    policytext[i] = policytext[i].strip()

# make a list of dictionaries for dumping to a yaml file
dict_file = []

for i in range(0, len(policytext)):
    line = policytext[i]
    dict_file.append({'segment_id' : i, 'segment_text' : line, 'sentence_annotations' : []})

with open(file_out_name, 'w') as out:
    documents = yaml.dump(dict_file, out)

#print(dict_file[0]["segment_text"])

policy.close()
out.close()

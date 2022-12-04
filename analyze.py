import yaml

def main():
    # Dictionaries of features to check for
    # 'review' is used as a keyword for both access and portability
    # need to add CCPA rights
    dict_policies = {"GDPR" : ["european union", "eu", "e.u.", "europe", "gdpr", "general data protection regulation"], "CCPA" : ["california", "ccpa"]}
    list_rights = [["Right_Deletion", ["delete", "deletion", "deleted", "erase", "erasure", "erased", "remove", "removed", "removal"]], 
    ["Right_Access", ["access", "review"]],
    ["Right_Rectification", ["rectify", "correct", "corrected", "correction", "rectification", "rectified", "update", "amend"]],
    ["Right_Restriction", ["restrict", "restriction", "stop"]],
    ["Right_Portability", ["request a copy", "receive a copy", "request to receive", "right to request", "right to receive", "review"]],
    ["Right_Objection", ["object", "objection"]],
    ["Right_Nondiscrimination", ["discriminate", "discrimination"]],
    ["LawfulProcessing", ["consent", "contract", "legal obligation", "legitimate interest", "vital interest", "public interest"]],
    ["DPO_Mentioned", ["data protection officer", "dpo"]]]

    GDPR_rights = ["Right_Deletion", "Right_Access", "Right_Rectification", "Right_Restriction", "Right_Portability", "Right_Objection",
    "LawfulProcessing", "DPO_Mentioned"]
    CCPA_rights = ["Right_Nondiscrimination"]

    # A list of lists that should probably be a list of dictionaries
    annotationList = []

    # Open the segmented policy file and read it in
    # In the current format SEGMENTS IS A LIST OF DICTIONARIES
    policyname = input("Enter the name of the file to read.\n")
    file_out_name = policyname.split('.')[0] + "_annotated.yml"

    policy = open(policyname, "r", encoding = "utf8")
    segments = yaml.load(policy, Loader=yaml.FullLoader)
    policy.close()

    # Convert all policy text to lowercase and store it in a separate array
    texts = []
    for i in range (0, len(segments)):
        texts.append(segments[i]['segment_text'])
    for i in range (0, len(texts)):
        texts[i] = texts[i].lower()

    # Scan each segment for phrases that indicate compliance
    for i in range (0, len(texts)):
        annotationList.append(makeAnnotations(texts[i], dict_policies, list_rights))
    
    #print(annotationList)

    # Add the annotations to the 'annotations' key in each segment's dictionary
    # Then dump them back out to a yml file
    # There is a visual problem with the yml dumping if two of a segment's dictionaries have the same values
    with open(file_out_name, 'w') as out:
        for i in range(0, len(segments)):
            #print(annotationList[i])
            segments[i]['sentence_annotations'] = annotationList[i]
            print(segments[i]['sentence_annotations'])
        documents = yaml.dump(segments, out)

# Make annotations on a single segment
def makeAnnotations(text, regulations, features):
    flagGDPR = False
    flagCCPA = False
    flagFound = False
    keywords = []
    annotations = {"GDPR": {}, "CCPA" : {}, "Unspecified" : {}}

    # if GDPR is mentioned anywhere
    if any(x in text for x in regulations["GDPR"]):
        flagGDPR = True
    # if CCPA is mentioned anywhere
    if any(x in text for x in regulations["CCPA"]):
        flagCCPA = True

    # cycle through all the features
    for i in range(0, len(features)):
        # cycle through all the keywords associated with each feature
        for j in range(0, len(features[i][1])):
            if features[i][1][j] in text:
                # Indicate the feature exists in the segment
                flagFound = True
                # Make a list of all the keywords found in the segment
                keywords.append(features[i][1][j])

        if flagFound == True:        
            # Add to GDPR dictionary if GDPR mention was found
            if flagGDPR == True:
                if not features[i][0] in annotations["GDPR"].keys():
                    annotations["GDPR"][features[i][0]] = keywords
            # Add to CCPA dictionary if CCPA mention was found
            if flagCCPA == True:
                if not features[i][0] in annotations["CCPA"].keys():
                    annotations["CCPA"][features[i][0]] = keywords
            # Otherwise, add to unspecified
            if (flagGDPR == False) and (flagCCPA == False):
                if not features[i][0] in annotations["Unspecified"].keys():
                    annotations["Unspecified"][features[i][0]] = keywords
        keywords = []
        flagFound = False

    #print(annotations)
    return annotations

def reportCompliance(annoList):
    pass

# features is a list of lists
# list_rights = [["Right_Deletion", ["delete", "deletion", "erase", "erasure"]]
#    ["Right_Access", ["access"]]]
# features is the list
# features[i] is a list of a practice and associated keywords
# features[i][0] is the name of the practice
# features[i][1] is the list of keywords
# features[i][1][j] is a keyword
main()
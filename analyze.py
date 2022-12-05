import yaml

def main():
    # Dictionaries of features to check for
    dict_policies = {"GDPR" : ["european union", "eu", "e.u.", "europe", "gdpr", "general data protection regulation"], "CCPA" : ["california", "ccpa"]}
    list_rights = [["Right_Deletion", ["delete", "deletion", "deleted", "erase", "erasure", "erased", "remove", "removed", "removal"]],
    ["Right_Access", ["access", "review"]],
    ["Right_Rectification", ["rectify", "correct", "corrected", "correction", "rectification", "rectified", "update", "amend"]],
    ["Right_Restriction", ["restrict", "restriction", "stop"]],
    ["Right_Portability", ["request a copy", "receive a copy", "request to receive", "right to request", "right to receive", "a copy"]],
    ["Right_Objection", ["object", "objection"]],
    ["Right_Know", ["know", "access", "shine the light", "disclose"]],
    ["Right_Nondiscrimination", ["discriminate", "discrimination", "penalize"]],
    ["Lawful_Processing", ["consent", "contract", "legal obligation", "legitimate interest", "vital interest", "public interest"]],
    ["DPO_Mentioned", ["data protection officer", "dpo"]],
    ["Sale_OptOut", ["do not sell my personal information", "do not sell", "do not share", "opt out of any sales", "opt out of the sale", "opt out of sales"]]]

    GDPR_rights = ["Right_Deletion", "Right_Access", "Right_Rectification", "Right_Restriction", "Right_Portability", "Right_Objection",
    "Lawful_Processing", "DPO_Mentioned"]
    CCPA_rights = ["Right_Nondiscrimination", "Right_Deletion", "Right_Know", "Sale_OptOut"]
    Unspecified_rights = ["Right_Deletion", "Right_Access", "Right_Rectification", "Right_Restriction", "Right_Portability", "Right_Objection",
    "Lawful_Processing", "DPO_Mentioned", "Right_Nondiscrimination", "Right_Know", "Sale_OptOut"]

    # A list of dictionaries of features
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
            #print(segments[i]['sentence_annotations'])

        # Generate the compliance report
        segments.insert(0, {'compliance_report' : reportCompliance(annotationList, GDPR_rights, CCPA_rights, Unspecified_rights)})
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

# Generate a compliance report based on the annotations made
# BUG: Instance counter is sometimes short by one (see rectification and right to know in policy 1)
def reportCompliance(annoList, gdpr_rights, ccpa_rights, unspecified_rights):

    CCPArightsCounter = {"Right_Nondiscrimination" : 0, "Right_Deletion" : 0, "Right_Know" : 0, "Sale_OptOut" : 0}
    GDPRrightsCounter = {"Right_Deletion" : 0, "Right_Access" : 0, "Right_Rectification" : 0, "Right_Restriction" : 0, "Right_Portability" : 0, "Right_Objection" : 0, "Lawful_Processing" : 0, "DPO_Mentioned" : 0}
    CCPArightsSum = 0
    GDPRrightsSum = 0

    # cycle through all the annotation dictionaries (one for each segment)
    for i in range (0, len(annoList)):
        # cycle through all the GDPR rights
        for j in range(0, len(gdpr_rights)):
            if gdpr_rights[j] in annoList[i]["GDPR"]:
                GDPRrightsCounter[gdpr_rights[j]] += 1
        # cycle through all the CCPA rights
        for k in range(0, len(ccpa_rights)):
            if ccpa_rights[k] in annoList[i]["CCPA"]:
                CCPArightsCounter[ccpa_rights[k]] += 1
        # unspecified rights handling
        for l in range(0, len(unspecified_rights)):
            if unspecified_rights[l] in annoList[i]["Unspecified"]:
                if unspecified_rights[l] in gdpr_rights:
                    # add it to the gdpr list
                    GDPRrightsCounter[unspecified_rights[l]] += 1
                if unspecified_rights[l] in ccpa_rights:
                    # add it to the ccpa list
                    CCPArightsCounter[unspecified_rights[l]] += 1

    # Sum up how many of the CCPA rights were found
    for key in CCPArightsCounter.keys():
        if CCPArightsCounter[key] > 0:
            CCPArightsSum += 1

    # Sum up how many of the GDPR rights were found
    for key in GDPRrightsCounter.keys():
        if GDPRrightsCounter[key] > 0:
            GDPRrightsSum += 1

    complianceReport = {'GDPR Rights Instances' : GDPRrightsCounter, 'CCPA Rights Instances' : CCPArightsCounter, 'GDPR Compliance Rate' : (GDPRrightsSum/8) * 100, 'CCPA Compliance Rate' : (CCPArightsSum/4) * 100}

    return complianceReport

# features is a list of lists
# list_rights = [["Right_Deletion", ["delete", "deletion", "erase", "erasure"]]
#    ["Right_Access", ["access"]]]
# features is the list
# features[i] is a list of a practice and associated keywords
# features[i][0] is the name of the practice
# features[i][1] is the list of keywords
# features[i][1][j] is a keyword
main()

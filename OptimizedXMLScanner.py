from lxml import etree
import json
from dotenv import load_dotenv

load_dotenv()


# Load the dictionaries
def load_json():
    with open("MyDictionaries.json") as json_file:
        data = json.load(json_file)
    return data


my_dictionaries = load_json()
docs = []


class CustomXMLLoader:
    def load(self, file_path: str):
        
        with open(file_path, 'rb') as f:
            xml = f.read()
        
        root = etree.fromstring(xml)

        # badSet = {"FundingInstrumentType", "AdditionalInformationOnEligibility", "AgencyCode", "PostDate", "CloseDate", "LastUpdatedDate", "Version", "GrantorContactEmailDescription", "CostSharingOrMatchingRequirement", "ArchiveDate", "AdditionalInformationText", "GrantorContactEmail", "GrantorContactEmailDescription", "GrantorContactText"}

        goodSet = {"OpportunityID", "OpportunityTitle", "OpportunityNumber", "OpportunityCategory", "CategoryOfFundingActivity", "EligibleApplicants", "CFDANumbers", "AgencyName", "AwardCeiling", "Description", "AdditionalInformationURL", }
        
        for child in root:
            archive_date = child.find(
                "{http://apply.grants.gov/system/OpportunityDetail-V1.0}ArchiveDate"
            )
            if archive_date is not None and archive_date.text is not None:
                if int(archive_date.text[-4:]) < 2024:
                    # print("Old Archive Date: " + archive_date.text)
                    continue
            
            close_date = child.find(
                "{http://apply.grants.gov/system/OpportunityDetail-V1.0}CloseDate"
            )
            if close_date is not None and close_date.text is not None:
                if int(close_date.text[-4:]) < 2024:
                    # print("Old Close Date: " + close_date.text)
                    continue

            funding_instrument_type = child.find(
                "{http://apply.grants.gov/system/OpportunityDetail-V1.0}FundingInstrumentType"
            )
            if funding_instrument_type is not None and funding_instrument_type.text is not None:
                if funding_instrument_type.text != "G":
                    print("Not a grant")
                    continue
            
            myString = ""
            opportunityID = "Not Found"
            
            for subchild in child:
                thisTag = subchild.tag.split("}")[-1]
                if thisTag in goodSet:
                    print("Goodset caught")
                    if thisTag == "OpportunityID":
                        opportunityID = subchild.text
                    if thisTag in my_dictionaries: 
                        if subchild.text in my_dictionaries[thisTag]:   
                            subchild.text = my_dictionaries[thisTag][subchild.text]
                            myString+=("The " + thisTag + " is " + subchild.text + ". | ")
                            # print(subchild.tag)
                        else:
                            print("Something went wrong")
                            print(subchild.text)
                            print(thisTag)
                    else:
                        myString+=("The " + thisTag + " is " + subchild.text + ". | ")
                        # print(subchild.tag)
            print(opportunityID)
                
                    
            doc = {"page_content": myString, "opportunity_id": opportunityID}
            docs.append(doc)
        return docs

# xml_file_path = "GrantsDBExtract20240607v2.xml"
xml_file_path = "GrantsDBExtract20240729v2.xml"
# xml_file_path = "test.xml"
loader = CustomXMLLoader()
documents = loader.load(xml_file_path)



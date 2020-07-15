word_lists = {
    "age_words" : (("age", "birthday", "dob"),
                    "hasAge"),

    "behaviour_words" : (("behaviour", "personality", "myers", "opinion"),
                    "hasBehaviourData"),

    "body_words" : (("body", "height", "weight", "size"),
                    "hasBodyStatistics"),

    "contact_words" : (("contact", "phone", "email"),
                    "hasContactInformation"),

    "criminal_words" : (("criminal", "jail"),
                    "hasCriminalActivity"),

    "doctor_words" : (("doctor", "consult"),
                    "hasDoctorConsultationsData"),

    "ethnic_words" : (("language", "race", "community", "accent", "dialect", "immigrant", "religion"),
                    "hasEthnicityData"),

    "health_words" : (("health", "medical"),
                    "hasHealthData"),

    "income_words" : (("income", "salary"),
                    "hasIncomeData"),

    "loan_words" : (("loan"),
                    "hasLoanRecords"),

    "location_words" : (("address", "city", "location", "resident"),
                    "hasLocationData"),

    "name_words" : (("name"),
                    "hasName"),

    "physical_words" : (("gender", "disability", "colour", "skin", "hair", "tattoos", "piercings"),
                    "hasPhysicalCharacteristics"),

    "politics_words" : (("politics"),
                    "hasPoliticalOpinions"),

    "religion_words" : (("religion"),
                    "hasReligion"),

    "tracking_words" : (("advertisement", "history", "browser", "search", "tracking"),
                    "hasUserTrackingData")
}

#for word_tuple in word_lists.values():

ans = [word_tuple[1] for word_tuple in word_lists.values() if "dob" in word_tuple[0]][0]

print(f"\n\nANS: {ans}\n")

# members-by-interest

Members of congress vary in many ways, from their background, to their party, to the types of areas they represent. Another important difference is that each member has their own set of personal interests that they bring to their work.

Analysts from the Congressional Research Service look at each bill and resolution and assign them terms from two controlled vocabularies: Policy Area terms and Legislative Subject Terms. The former is a broad overview of the topic of a bill (only one heading is assigned), while the latter is much more granular.

There is not really a great open API for matching (co)sponsorships to subjects to memebers, so this uses a custom API -- [fetch-bill-statuses](https://github.com/esperr/fetch-bill-statuses).
Using the bulk bill status system, information about individual bills are downloaded. Then their subject and policy terms are extracted and matched to member(s) sponsoring and cosponsoring each bill. The resulting data is displayed in two ways — either as a ranked list of members for a given subject, or a graph showing what an individual member is most uniquely engaged with.

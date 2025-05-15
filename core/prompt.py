from langchain_core.prompts import ChatPromptTemplate

DATA_GENERATION_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "assistant",
            """
            You are a multilingual generation agent. You generate code-switched text 
            based on the user’s instructions. Follow these guidelines:


            1. Language Roles:
            - The Matrix Language (dominant language) is {first_language}. 
            - The Embedded Language (secondary language) is {second_language}.


            2. Code-Switching Functions:
            - Directive: Include or exclude certain listeners.
            - Expressive: Show identity, cultural connection, or emotion.
            - Referential: If a concept is easier to express in the other language.
            - Phatic: Repeat or emphasize by switching languages.
            - Metalinguistic: Quoting or commenting on a phrase in the other language.
            - Poetic: Jokes or wordplay in the embedded language.
            - The function is {cs_function}

            3. Code-Switching Types:
            - Intersentential: Switch languages across sentence boundaries.The switch occurs at sentence or clause boundaries. The speaker finishes one sentence (or clause) in Language A, then starts the next sentence (or clause) in Language B. This form often appears when the speaker wants to address different audiences or emphasize particular parts of the conversation. It can be used for directive functions (e.g., to include/exclude certain listeners), or for phatic emphasis of entire sentences.
              - Examples: English to Spanish,“I have a big project due tomorrow. ¿Puedes ayudarme?”(English sentence first, then Spanish question.)
              - Examples: Hindi to English,“Maine kal tumhe phone kiya tha. But you didn’t pick up!”(Hindi clause followed by an English clause.)
              - Examples: Chinese to English ,“今天天氣真的好好。 I think we should go for a walk.”(Chinese sentence about the weather, then an English suggestion.)
              - Examples: Filipino (Tagalog) to English,““Gusto kong kumain sa labas mamaya. Let’s try that new restaurant!””(Tagalog statement, then an English invitation.)
              - Use one full sentence in the matrix language, then start a new sentence in the embedded language.
              - Each entire sentence is generally in one language, though small connectors (like “and,” “but”) may appear.
            - Intrasentential: Switch languages within a single sentence.
              - This is often more complex syntactically, because the switch must respect each language’s grammar constraints (like subject-verb-object ordering, morphological rules, etc.).
              - Commonly used when a certain term or phrase is better expressed in the second language, or to add emphasis (expressive function).
              - Examples: English to Portuguese,“I don’t know o meu lugar nesse mundo.”(Partial phrase in Portuguese: “my place in this world.”)
              - Examples: Chinese to English,“我老是去那家 coffee shop，因为那里真的很 peaceful，而且vibe也不错。”(Chinese sentence about the son, then an English statement.)
              - Within a single sentence, embed a short phrase or clause in the second language (e.g., for an object, an adjective, or a common expression).
              - Remind the model to maintain grammatical coherence; e.g., do not place an English determiner in a position that violates the word order rules of the main language.
            - Extra-sentential / Tag switching: A short tag, filler, or interjection from the second language is inserted into an otherwise single-language utterance. Common examples are “right?”, “you know?” or discourse markers like “anyway,” “well,” “deshou?”, “baka,” etc.
              - Tag-switching is the simplest and most common pattern in everyday speech, because a speaker might unconsciously insert a familiar filler or confirmational phrase from their second language.
              - Often used for phatic or expressive functions, adding flavor or emotion to the conversation.
              - Examples: English (main) + Japanese (tag),“It’s a good movie, deshou?"
              - Examples: Chinese (main) + English (tag),“好辛苦呀, oh my gosh!”
            - The type is {cs_type}

            4. Ensure your output follows these constraints:
            - The matrix language proportion is {cs_ratio}
            - The syntax remains correct in both languages. (Observe free morpheme constraint & equivalence constraint.)
            - Make it sound natural to bilingual speakers (avoid unnatural mixing).
            - Respect socio-cultural norms (correct borrowed words, e.g., Chinese might use '士多啤梨' instead of '草莓').

            5. Output must be in JSON format with keys: [topic, instances].
            - 'instances' is an array of generated sentences (for single-turn)
            OR an array of message pairs if multi-turn.

            6. Language Requirements:

            - Tense: {tense}
            - Perspective: {perspective}

            7. Persona:
            - Gender: {gender}
            - Age: {age}
            - Education Level: {education_level}

            8. News Article:
            - If news_article is provided, you must generate code-switched text based on the news article,like review/opinions/conversations etc...
            - News Article: {news_article} \n

            9. The conversation type is {conversation_type}

            


            **Example Output Structure format** (for a multi-turn example in Cantonese-English Mixed Language):
            {{
                "instances": [
                "XXXXX？",
                "XXXXX！",
                "XXXXX。",
                "XXXXX。"
                ],
            }}

            Now,given the topic {topic}, and external information {mcp_result}, think carefully and produce your code-switched text.
            
            ### INTERNAL (do NOT reveal):
            1. Parse the {first_language} sentence into a dependency tree.
            2. Translate it into {second_language}.
            3. Align tokens between the two sentences.
            4. Locate all switchable spans that satisfy the Equivalence
                & Functional‑Head constraints; pick the best one.
            – Keep all intermediate notes private. 
            The below is the reference of the code-switching usage:
            ### END INTERNAL
            """,
        )
    ]
)


FLUENCY_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "assistant",
            """
            You are **FluencyAgent**. Your task is to evaluate the grammatical correctness and syntactic coherence of code-switched text. Specifically:

            1. **Check for code-switching constraints** from *Poplack (1980)*:
            - **Free Morpheme Constraint**: no switching between a bound morpheme (e.g., “-s” in English) and a free morpheme.
            - **Equivalence Constraint**: switches should occur where the two languages’ syntactic structures align.

            2. **Check for grammatical errors** or unnatural mixing of word orders between the matrix and embedded languages.

            3. **Output**:
            - A `fluency_score` (0 to 10).
            - A list of identified `errors` (if any), each with:
                - `description`
                - `constraint_violated` (e.g., mention “Free Morpheme Constraint,” “Equivalence Constraint,” or a known grammar rule)
            - A short `summary` of overall fluency.
            given the code-switched text {data_generation_result}.
            """,
        )
    ]
)

NATURALNESS_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "assistant",
            """
            You are **NaturalnessAgent**. Your job is to evaluate how natural and authentic the code-switched text is from a *bilingual speaker’s perspective*:

            1. **Check typical code-switching usage**:
            - **Intersentential, Intrasentential, and Tag Switching**.
            - Whether the sentence sounds like something real bilingual speakers would say.

            2. **Consider factors from *Auer (1998)*:
            - **Inter-sentential**: switching at sentence boundaries.
            - **Intra-sentential**: switching in the middle of a sentence.
            - **Tag switching**: short tags or phrases in the embedded language.

            3. **Output**:
            - A `naturalness_score` (0 to 10).
            - A list of `observations` about unnatural or awkward phrases, if any.
            - A `summary` describing how natural the code-switching is overall.           
            given the code-switched text {data_generation_result}.
            """,
        )
    ]
)

CS_RATIO_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "assistant",
            """
            You are **CSRatioAgent**. You evaluate the *Code-Switching Ratio* (CS-Ratio) in given text. Specifically:

            1. **Check the proportion** of matrix language vs. embedded language:
            - Count tokens/words for each language.
            - Compare to a desired ratio (e.g., 70% matrix, 30% embedded) if provided.

            2. **Output**:
            - A `ratio_score` (0 to 10) reflecting how well it matches the target ratio.
            - A `computed_ratio` or breakdown: e.g., "66% : 34%".
            - A `notes` field listing any ratio-related observations.

            given the desired ratio: {cs_ratio}
            given the code-switched text {data_generation_result}.
            """,
        )
    ]
)

SOCIAL_CULTURAL_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "assistant",
            """
            You are **SocioCulturalAgent**. Your goal is to ensure that the code-switched text respects *cultural norms* and uses *correct borrowed words* or expressions.

            1. **Check culture-specific vocabulary**:
            - For Cantonese: "士多啤梨" instead of "草莓" for "strawberry," etc.
            - For Spanish: Keep "taco" in Spanish, do not forcibly translate.
            - Avoid offensive or extremely unnatural usage in local contexts.

            2. **Output**:
            - A `socio_cultural_score` (0 to 10).
            - An array of `issues` if you find any unfit usage:
                - `description`
            - A short `summary` with your overall assessment.
            given the code-switched text {data_generation_result}.
            """,
        )
    ]
)

REFINER_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "assistant",
            """
            You are **RefinerAgent**. Your task is to refine the code-switched text based on the comments from the FluencyAgent, NaturalnessAgent, CSRatioAgent, and SocioCulturalAgent:

            1. **Fluency**:
            - Check for grammatical errors or unnatural mixing of word orders between the matrix and embedded languages.
            
            2. **Naturalness**:
            - Check if the sentence sounds like something real bilingual speakers would say.

            3. **CS Ratio**:
            - Check the proportion of matrix language vs. embedded language.

            4. **SocioCultural**:
            - Check if the code-switched text respects cultural norms and uses correct borrowed words or expressions.

            Here are the comments : {summary}

            Please refine the code-switched text based on the comments.
            """,
        )
    ]
)

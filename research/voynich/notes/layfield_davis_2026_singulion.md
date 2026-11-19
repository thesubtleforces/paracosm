# Singulion Structure and the Voynich Manuscript

Colin Layfield and Lisa Fagin Davis, *Digital Medievalist* 19 (2026). https://doi.org/10.4000/16k0a

Text reproduced under the article's licence, CC BY 4.0 (text only; figures and formula images are not included).
Retrieved 19 November 2026 from https://journals.openedition.org/digitalmedievalist/2331 and reduced to plain text:
navigation, export widgets and image embeds were removed. Table markup is as scraped.

---

## Abstract

The Voynich manuscript has baffled linguists, cryptologists, computer scientists and the general public for over a century and has thus far refused to give up its secrets. Recent work on the manuscript (Layfield & Davis, 2026) has shown that the manuscript shows some degree of coherence and flow that echoes what we would expect in other known documents, but some findings were still unexplained. The present work is a continuation of those experiments where we, again, use Latent Semantic Analysis (LSA) to explore the text recorded on pages, leaves, bifolia, and quires of the manuscript, looking for patterns that may be evidence of the original structure of the manuscript. Through comparisons with known texts such as the _Aberdeen Bestiary_ and the _Speculum Humanae Salvationis_ we have found strong evidence that the Voynich manuscript is not meant to be bound in quires at all (as is the norm) but, instead, was originally a collection of individual bifolia meant to be read in sequence (called “singulions”). Additional investigation was undertaken to hypothesize the original sequence of bifolia, if any.

## Index terms

### Keywords:

Latent Semantic Analysis; Voynich Manuscript; Codicology; Medieval Manuscripts; Data Analytics

## Outline

Introduction

Research Questions

Latent Semantic Analysis

Manuscript Structure

Method

Results & Analysis

Quire Experiments

Bifolia Experiments

Bifolia Re-ordering Experiments

Discussion

Conclusions

## Author’s notes

The authors did not receive support from any organization for the submitted work.

## Full text


# Introduction

- 1The entire manuscript may be viewed here: https://beinecke.library.yale.edu/collections/highlights/ (...)
- 2E.g. Bowern and Lindemann 2021.

1The enduring mystery of the Voynich Manuscript (a.k.a. Yale University, Beinecke Rare Book & Manuscript Library MS 408) lies with its illustrations, certainly, but also with its text, entirely written in a unique set of symbols of unknown origin and meaning. 1 The results of recent material testing revealed no evidence that the manuscript is anything other than an early fifteenth-century manuscript, likely from Central or Southern Europe. Recent linguistic and computational analyses have revealed more about this famously-unread manuscript, including topical patterns, grammatical structures, and orthographic rules, all of which are moving the community of Voynich researchers closer to an understanding of the content of the codex. 2 There are other anomalous features of the manuscript that call out for exploration, however. At first glance, the Voynich Manuscript seems to be structured like any other medieval manuscript. But as with most Voynich topics of inquiry, the closer one looks, the more complicated things become. How can we explain the observation that several illustrations cross the internal gutter to emerge onto their conjoint page? Or the fact that scribal work in the herbal section is organized by bifolia rather than solely by topic, quire, or page? Why is the current structure of the manuscript so inconsistent? And how do these anomalies impact attempts to render the manuscript legible? This paper will consider these questions and present a novel way of addressing some of the linguistic and analytical problems posed by the Voynich Manuscript.

2To engage with these questions, it is important to first understand how medieval parchment manuscripts are constructed. The animal skin used for the manuscript’s substrate (calf, in the case of the Voynich) was carefully prepared over the course of several weeks – cleaned, soaked, stretched, and scraped, stretched and scraped again and again until it was thin and supple. Once the skin was ready, it was cut into rectangles – the size and number depending on the size of the animal and the intended size of the book. For the Voynich Manuscript, most of these sheets were around 225 x 320 mm, and there were likely eight such sheets per skin. The sheets – called _bifolia_ – were folded in half to create two leaves, or _folios_, whose relationship to one another is described as _conjoint_. Each side of a folio is a _page_, and the two sides of a leaf are said in what follows to be _confoliate_ with one another. The first side to be read is the _recto_, and the other is the _verso_. Bifolia were nested before writing to create small notebooks called _quires_. After writing and decorating, the quires were stacked and sewn together between covers to create the final bound book. A quire of five nested bifolia is called a _quinion_, four is a _quaternion_, three is a _ternion_, two a _binion_, and a quire with just one bifolium is called a _singulion_. Most early manuscripts structured in this way are composed of quires of four or five bifolia.

3As currently configured, the bifolia of the Voynich Manuscript are sequenced like most medieval manuscripts, in quires of nested bifolia. The structure of the manuscript can be discerned in part because of folio numbers that were added before the loss of fourteen leaves, and sequential quire numbers in the lower margin of the final verso of most quires that were added before the loss of two gatherings. The current structure can be summarized by a collation statement that lays out the components of each of the eighteen extant quires, where the superscript number expresses the number of leaves in each quire:

418, 28-1 (lacking f. 12), 3-78, 810-6 (lacking ff. 59-64), 9-112, 122-1 (lacking f. 74), 1310, 142, 154, \[162 (ff. 91/92) lacking\], 174, \[182 (ff. 97/98) lacking\], 194, 2014-2 (lacking ff. 109-110)

- 3In what follows, conjoint bifolia are indicated by two folio numbers separated by a vertical line, (...)

5A more complex story emerges with a deeper examination of the collation statement. The quires vary dramatically in their composition, with one, two, four, five, and even (formerly) seven bifolia. Such inconsistency is quite unusual. After a detailed examination, Yale conservation officer Paula Zyats recently concluded that there was no sign of more than one sewing (Zyats 2016, 25-26), and that the original sewing dated from the late Gothic period (ca. 1400-1500). This suggests that the bifolia have been bound in their current sequence since sometime in the fifteenth century. However, both physical and data evidence indicate that the bifolia are not in their intended, original sequence. Generally, it would be expected that the bifolia would be nested into quires before being written and decorated. Evidence of such a process would include, for example, scribal transitions occurring between non-conjoint facing pages, consecutive quires, or consecutive sections; or illustrative components mistakenly crossing from the verso of one page to the (non-conjoint) facing page. The evidence in the Voynich manuscript contradicts this expected sequence of production. In fact, the evidence presented below suggests in sum that the manuscript was not originally intended to be structured in quires of nested bifolia at all but rather as a series of stacked bifolia, the single-bifolium quires called _singulions_. 3

6The most obvious evidence in support of this argument are the well-documented examples of illustrations crossing the gutter between non-consecutive conjoints, such as the two streams in the center gutter margin of folio 78v that cross the gutter to emerge in the gutter margin of the conjoint folio 81r (fig. 1).

Figure 1

Folio 78v and 81r

(images courtesy of the Beinecke Rare Book & Manuscript Library)

7Less obvious, but still evidentiary, are examples on conjoint bifolia 10v\|15r (the splashed stain), 33v\|40r (the blue petals), 58v\|65r (a bit of green leaf), and 76v\|83r (the nymph’s right arm in the upper gutter) (Pelling 2006, 55 and 62). In each case, this visual evidence suggests that the bifolia were decorated before being nested and bound, an extremely unusual sequence of production.

8There is also evidence that the bifolia were individually _written_, not just illustrated, before being nested and bound. In past work, co-author Davis has argued that the Voynich Manuscript was written by five different hands (Davis, 2020) and (2022)). In the 1970s, Voynich researcher Prescott Currier observed that there were at least two scribes at work in the herbal section, and that each of the scribes consistently wrote both sides of any particular page (D’Imperio, 1978), 45). Currier was also the first to observe linguistic patterns that correlate with his Scribe 1 and Scribe 2 in the herbal section, patterns commonly referred to as “Language A” (Scribe 1) and “Language B” (the other scribes). The distinctions between Language A and Language B will be explored below.

- 4There is also one page - 115r - on which two scribes (2 and 3) collaborated.

9Davis’ work concurs with this observation, although by considering the bifoliate structure of the manuscript she uncovered a deeper pattern. When scribal output is mapped onto the codicological structure of the manuscript, we can observe that, with only two exceptions (bifolia 57\|66 and 85\|86), all four pages of each of the fifty-two extant bifolia were written by a single scribe (Davis, 2020). 4 For example, Quire 4 is comprised of four nested herbal bifolia: 25\|32, 26\|31, 27\|30, and 28\|29. All four pages of bifolium 26\|31 (26r, 26v, 31r, and 31v) were written by Scribe 2. The other three bifolia were entirely written by Scribe 1. Throughout the herbal section, these single-scribe bifolia are nested such that the scribal corpora are mixed by bifolia within quires, an unprecedented structure that adds to the evidence suggesting that the bifolia were completely decorated and written before being nested. If each bifolium is a unit meant to read as four consecutive pages (e.g. 10r, 10v, 15r, 15v), then the current nested structure (e.g. 10r, 10v, 11r, 11v) is incorrect. The manuscript’s bifolia are no longer in their intended sequence. Because offsets elsewhere in the manuscript (places where pigment from one page has rubbed off onto the parchment of the facing page) indicate that it has been in its current state for centuries, and there is evidence of only one set of wooden covers (likely fifteenth century) before the present limp vellum (likely nineteenth century), we can conclude that the initial fifteenth-century binding was itself the mis-binding, and that whomever was responsible for the current configuration was not able to “read” the manuscript.

- 5In the center of a quire, the facing pages are also conjoint.

10This contention based on codicological and paleographic evidence is supported by data analytics. In the next section, we will employ Latent Semantic Analysis (LSA) to demonstrate 1) that LSA is a reliable predictor of text similarity in general and thus, by extension, in the Voynich Manuscript, and 2) that the methodology can be used to hypothesize the intended singulion sequences in the Voynich Manuscript. In what follows, it is important to remember that, within a quire, each page is codicologically related to three other pages: the other side of its folio, called _confoliate_ (as in, “folio 2r is confoliate with folio 2v.”); the next page of the opening, called _facing_ (as in “folio 2v faces folio 3r”); and the page to which it is attached, called _conjoint_ (as in, “folio 2v is conjoint with folio 7r”). 5 All three of these terms – confoliate, facing, and conjoint – will be used throughout the remainder of this essay. The confoliate and conjoint relationships are immutable, regardless of the sequence of bifolia within a quire. The facing pages, however, will change as bifolia are shuffled. This codicological law is critical for interpreting the LSA data.

# Research Questions

11This paper will explore two Research Questions (RQs):

1. Is there data evidence supporting the hypothesis that the Voynich Manuscript is misbound and was originally intended to be a loose collection of singulions?

2. If we treat the manuscript as a collection of singulions, can we infer the intended sequence?

12To test the hypothesis that the individual bifolia of the manuscript were intended to be unbound singulions, we will employ Latent Semantic Analysis/LSA (Deerwester _et al._, 1990) as a tool for comparing blocks of text in the MS. Any two compared blocks of text return a similarity score: the higher the score, the higher the similarity. By applying LSA to the pages, leaves, and bifolia of the Voynich Manuscript, we will look for patterns that may help discern whether the pages are meant to read as individual bifolia or, as in most manuscripts, nested and bound in quires.

13If the manuscript was meant to be nested and bound in quires, we would expect to see high confoliate and facing scores due to the immediate proximity of the pages to one another. By extension, we expect the similarity score between two conjoint pages (by which we mean the interior pages of a bifolium) to be relatively low because in a nested quire all of the conjoints (except for the central bifolium) are separated by a number of intervening bifolia; in other words, the texts on those conjoint pages are not adjacent. The interior pages of the central conjoint, however, should have a higher similarity score as those pages are both conjoint and consecutive.

- 6Aberdeen University Library MS 24 <https://www.abdn.ac.uk/bestiary/>
- 7Harvard University (Cambridge, Massachusetts, United States of America), Houghton Library MS Lat 12 (...)

14We test this hypothesis by examining the confoliate and conjoint scores of the Voynich Manuscript bifolia to see if they behave in ways that are similar to one another. With statistical testing, we can confirm whether the scores are likely to have come from a similar distribution or not, which would imply that the conjoint pages are meant to be read sequentially (singulions rather than nested quires). To establish the efficacy of the methodology, we will perform similar analyses on two manuscripts of known texts in order to verify how confoliate and conjoint scores should behave. With known texts that are bound in quires we would expect to see the scores comparing interior conjoint pages to be significantly lower than their confoliate scores as the former pages are not consecutive (again, with the exception of the central bifolium), while the latter are. If the above behaviours are confirmed, we can apply the methodology to the bifolia of the Voynich Manuscript to investigate if the Voynichese text behaves as a manuscript of nested bifolia should. The two benchmark manuscripts are the _Aberdeen Bestiary_ 6 (13th-century medieval Latin) and a manuscript of the _Speculum Humanae Salvationis_ 7 (14th-century medieval Latin). We are using the cleaned version of the _Speculum_ from (Layfield & Davis, 2026) with redundant text at the beginning of each chapter removed in pre-processing.

15If we consider the Voynich Manuscript as a collection of singulion bifolia, might it be possible to hypothesize their correct sequence? Given the coherence of several of the illustrative sections (as demonstrated in Layfield & Davis, 2026), we will consider selected bifolia in groups organized by illustrative content:

Table 1

- 8F. 116v is not part of the primary text and will not be considered here.

|     |     |     |     |     |
| --- | --- | --- | --- | --- |
| Section | Scribe(s) | Languages | Quire Structure | No. of extant bifolia |
| Botanical (ff. 1r-66v) | 1, 2, 3, 5 | A, B | 18, 28-1 (lacking f. 12), 3-78, 810-6 (lacking ff. 59-64) | 30 |
| Cosmological/Astrological diagrams (ff. 67r-74v) | 4 | B | 9-112, 122-1 (lacking f. 74) | 4 |
| Biological (ff. 75r-84v) | 2 | B | 1310 | 5 |
| Rose foldout (ff. 85r-86v) | 2, 4 | B | 141 (a single large sheet) | 1 |
| Pharmaceutical/Recipes (ff. 87r-102v) | 1, 3 | A, B | 154, \[16: lacking\], 178-4 (lacking ff. 91-92, 97-98), \[18: lacking\], 194 | 6 |
| Stars (ff. 103r-116r) 8 | 3, 2 | B | 2014-2 (lacking ff. 109-110) | 6 |

Summary of the Contents and Structure of the Voynich Manuscript

16The experiment for this RQ involves calculating the similarity scores for facing pages in the current (quire-based) structure and comparing them to all permutations of the facing scores for individual singlion bifolia. For example, in the current structure, folio 1v faces folio 2r, but as a singulion, folio 1v would be followed by its conjoint, folio 8r (see figure 2). Can we find a sequence of singulions that returns higher scores than the current nested quire structure, and can we then conclude that the highest scores may represent the correct sequence of bifolia?

Figure 2

Bifoliate Structure of Quire 1 (Bifolia 1\|8, 2\|7, 3\|6, 4\|5)

# Latent Semantic Analysis

17The technique we will use to analyse the text is Latent Semantic Analysis (LSA). This is a method from the world of Information Retrieval and was originally used for search functions by comparing a query with a collection of documents to find the most similar match. In practice it can compare any two pieces of text and derive a similarity score based on the words that are present and how related they are to one another and how they are used in general. This is derived from the semantic space that is generated from a collection of documents to learn the relationships between words (patterns of usage, co-occurrences and so forth) and their underlying latent relationships. For further details see (Deerwester _et al_., 1990).

18It is worth exploring _why_ we would use a 35-year-old technique to study the Voynich Manuscript. While Natural Language Processing (NLP), Information Retrieval (IR) and Artificial Intelligence (AI) have all progressed significantly in the last few decades, the unique nature of the Voynich Manuscript continues to pose a significant roadblock to the performance of sophisticated analytics, as the entire Voynichese corpus consists of a mere 35,000 words. Most modern NLP and AI techniques make use of massive amounts of data to train a model (often measured in the billions of datapoints for modern Transformer architectures, for example ChatGPT, Gemini or Grok); the limited corpus of Voynichese forces us to rely on methods such as LSA that are proven to work fairly well on smaller datasets (Altszyler _et al_., 2017,dos Santos & Favero, 2015).

19The first step in LSA is preparation of the text. For the two known texts (the _Aberdeen Bestiary_ and the _Speculum Humanae Salvationis_) we perform the following steps: lowercasing, removal of any diacritics and punctuation, and stop-word removal. Stop-words are words that occur very frequently while adding little to the discourse and are therefore largely considered noise with techniques such as LSA. In English a stop word list would include words such as “the”, “and”, “of”, “an”, etc. As we cannot semantically identify the stop words that are contained in the Voynich text, we use a heuristic to determine stop words algorithmically for both the known texts and the Voynich text (in order to apply the same pre-processing rules to all three texts). The heuristic to generate this stop word list first sorts words in a text by their Term Frequency (TF) count in descending order. We use a window of size _w_ to calculate the average difference in TF between the first _w_ terms of our list. This window is shifted by 1 word and this difference is once again calculated. This repeats until the difference falls below a set threshold value of, say _v_. If it takes _x_ steps to reach this threshold then the first ( _w + x – 1_) words in the sorted TF list are selected as the stop words to use. We utilized a window of size 6 and a threshold of 3 to generate stop word lists for the three texts.The stop word lists generated can be found in Appendix 2.

- 9The transliteration files can be found here: https://www.voynich.nu/transcr.html

20A slightly different process must be employed to prepare the Voynich text. There are no obvious upper-case letters, punctuation, or diacritics, so that particular pre-processing step is unnecessary. We use the heuristic described above to generate a stop word list and remove them from the text. We also remove any words with an uncertain transcription, as indicated in the Voynich transliteration file (an ASCII-character, machine-readable transcription of the manuscript). The transliteration file follows the Intermediate Voynich MS Transliteration File Format (IVTFF) version 1.7 as defined in (Zandbergen, IVTFF – Intermediate Voynich MS Transliteration File Format – File Format 1.7.2020). This file format identifies uncertain characters and spaces as well as other anomalies in the transliteration, uncertain readings that we have removed in pre-processing. The Voynich transliteration file we are using is the ZL version 2a dated 17/03/2022, which is the most complete, consistent, and accurate transcription currently available. 9

21Once the text has been prepared, we produce a term-by-document matrix _A_ of _n_ rows and _m_ columns, where each row represents one Voynichese term (i.e. a group of symbols with a space on either side generally understood to represent a “word” or term), each column represents a “document” (i.e. a selection of text to be analyzed), and matrix entry _A_ _i,j_ is the Term Frequency (TF) count indicating the number of times term _i_ occurs in document _j_.

22We define a “document” as follows: For the _Aberdeen Bestiary_ and the _Speculum,_ we take the text in 40 word “chunks” (each of which is a document (column) in Matrix _A_) and process the text accordingly. The Voynich Manuscript is a little more complicated in that there are different categories of textual formats. The transliteration file indicates where text is considered _paragraph_ text, _radial_ text (text along the radius of a circular image) or _circular_ text (text written along the outside of a circular figure). For each page we treat each of these categories individually (to ensure any “document” created from them is from the same text type) and, again, partition it into documents of approximately size 40 (if it does not divide exactly into a multiple of 40 we create documents that are as close to 40, on average, as possible and disregard text components that are less than 20 words in length). We use the “chunk” size of 40 for consistency across the different texts used. In the _Speculum_, for example, there are no clear paragraph delineations whilst in the Voynich there is a paragraph-like structure present but it can vary in size dramatically. 40 seemed to be a good middle ground and worked well in our previous LSA experiments in (Layfield & Davis, 2026).

- 10We are using TF-IDF as we found it useful in our previous work on LSA on the Voynich (and other tex (...)

23Once matrix _A_ has been created it is weighted using the Term Frequency-Inverse Document Frequency (TF-IDF) formula 10. This ensures that frequent terms will have a lower weight than terms that are less common. So each element in _A_ is transformed as follows:

24Where _f_ _ij_is the TF value for term _i_ in document _j_, _n_ is the total number of documents and _df_ _i_ is the Document Frequency (DF) of term _i._ Document frequency of a term is the number of different documents in which the term occurs.

25Once the matrix has been created we apply Singular Value Decomposition (SVD), a matrix factorisation technique, resulting in:

26This can be visualised as:

Figure 3

SVD Matrix Factorisation

27The matrix of interest to us is the _D_ _T_matrix. Each column will correspond to a document from the original _A_ matrix. The _A_ matrix is sparse (mostly zeroes) whereas the _D_ _T_ matrix will have almost entirely nonzero values. The next step is dimensional reduction, reducing the dimensionality of the matrices to a value _k_. This value _k_ would replace the value _r_ in Figure 3 so each document vector in _D_ _T_ (column) will now have _k_ dimensions. The reduction of the dimensionality to _k_ filters out some of the noise in the space to reveal what may be underlying latent relationships of interest. Large semantic spaces typically will use a value of 300 or so but because the semantic spaces we will be generating are much smaller, we will be using values of 75. See Appendix 1 for the method used for dimensional selection as well as a discussion of other semantic space design decisions.

28We use cosine as the comparison/scoring operator. To compare two documents in the _D_ _T_ matrix, then, we need to generate two vectors on which to perform the cosine operation. So, to compare documents _i_ and _j_ (representing columns in _D_ _T_), we would generate their vectors as follows:

29Each document vector is scaled by the _S_ matrix (diagonal matrix of singular values) so that the cosine operator can be carried out directly on the two generated vectors. We can also apply the same operation to an arbitrary selection of text _d_ (essentially an additional virtual column of _A_ that we created that indicates the terms present in the document we want to compare) after folding the document into _D_ _T_ as an additional column. To carry out the transformation on _d_, we calculate the following:

- 11A cosine value has the range \[-1.0, 1.0\]

30Now can be treated as any other column in _D_ _T_. The cosine operator is used to compare two documents (vectors) and we view the value as the semantic similarity between them. The higher the cosine, the higher the score, and the more commonalities there are between the two documents. 11 We can confidently say this with texts such as the _Aberdeen Bestiary_ and the _Speculum_, as we can refer back to the original texts to test the reliability of the method. For the Voynich, we interpret the scores as a measure of how text is being used between the two documents - as we do not know yet if Voynichese represents a real language, we cannot say with certainty that the similarity is _semantic,_ as is it in the known texts. In our previous work, however, we demonstrated that the Voynich Manuscript behaves in a very similar way to known texts such as the _Aberdeen Bestiary_ (and others) in the coherence and flow of individual sections as defined in Table 1 above.

31Using the above approach we create _three_ different semantic spaces: the _Speculum_, the _Aberdeen Bestiary_, and the Voynich Manuscript. Table 2 records the sizes of the various semantic spaces. The number of terms indexed in each semantic space does not include stop words or unique - and therefore non-comparable - terms ( _hapax legomena_) as each term in the semantic space must have a document frequency of _at least_ two.

Table 2

|     |     |     |
| --- | --- | --- |
| **Semantic Space** | **Terms** | **Documents** |
| _Speculum_ | 3,697 | 809 |
| Aberdeen Bestiary | 4,607 | 876 |
| Voynich (Complete) | 2,161 | 606 |

Semantic Space Sizes

# Manuscript Structure

32Because we are conducting experiments on the relationships between text (an intellectual element) and bifolia (a physical element), we need to tabulate the codicological structure of the manuscripts we will be analysing. See Tables 3, 4, and 5 below for the quire structure of the _Aberdeen Bestiary_ and selected quires from the _Speculum_ manuscript in addition to the Voynich Manuscript itself (in each case, singletons have been excluded from the analysis as they do not have a conjoint for comparison). In Table 5, regarding the Voynich, brackets indicate missing bifolia or pages.

Table 3

|     |     |     |     |     |
| --- | --- | --- | --- | --- |
| Quire | Bifolios |
| 1 | 1\|6 | 2\|5 | 3\|4 |  |
| 2 | 7\|12 | 8\|11 | 9\|10 |  |
| 3 | 14\|18 | 15\|17 |  |  |
| 4 | 19\|24 | 20\|23 | 21\|22 |  |
| 5 | 25\|32 | 26\|31 | 27\|30 | 28\|29 |
| 6 | 33\|40 | 34\|39 | 35\|38 | 36\|37 |
| 7 | 41\|48 | 42\|47 | 43\|46 | 44\|45 |
| 8 | 49\|56 | 50\|55 | 51\|54 | 52\|53 |
| 9 | 57\|64 | 58\|63 | 59\|62 | 60\|61 |
| 10 | 65\|72 | 66\|71 | 67\|70 | 68\|69 |
| 11 | 73\|78 | 74\|77 | 75\|76 |  |
| 12 | 80\|87 | 81\|86 | 82\|85 | 83\|84 |

Quire/Biofolio Breakdown for Aberdeen Bestiary

Table 4

|     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- |
| Quire | Bifolios |
| 1 | 1\|12 | 2\|11 | 3\|10 | 4\|9 | 5\|8 | 6\|7 |
| 3 | 25\|36 | 26\|35 | 27\|34 | 28\|33 | 29\|32 | 30\|31 |
| 4 | 37\|48 | 38\|47 | 39\|46 | 40\|45 | 41\|44 | 42\|43 |

Quire/Bifolio Breakdown for Speculum (selected quires)

Table 5

|     |     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Section | Quire | Bifolios (missing leaves in brackets) |
| Botanical | 1 | 1\|8 | 2\|7 | 3\|6 | 4\|5 |  |  |  |
| 2 | 9\|16 | 10\|15 | 11\|14 | \[12\]\|13 |  |  |  |
| 3 | 17\|24 | 18\|23 | 19\|22 | 20\|21 |  |  |  |
| 4 | 25\|32 | 26\|31 | 27\|30 | 28\|29 |  |  |  |
| 5 | 33\|40 | 34\|39 | 35\|38 | 36\|37 |  |  |  |
| 6 | 41\|48 | 42\|47 | 43\|46 | 44\|45 |  |  |  |
| 7 | 49\|56 | 50\|55 | 51\|54 | 52\|53 |  |  |  |
| 8 | 57\|66 | 58\|65 | \[59\|64\] | \[60\|63\] | \[61\|62\] |  |  |
| Cosmological/Astrological | 9 | 67\|68 |  |  |  |  |  |  |
| 10 | 69\|70 |  |  |  |  |  |  |
| 11 | 71\|72 |  |  |  |  |  |  |
| 12 | 73\|\[74\] |  |  |  |  |  |  |
| Balneological | 13 | 75\|84 | 76\|83 | 77\|82 | 78\|81 | 79\|80 |  |  |
| Rose | 14 | 85\|86 |  |  |  |  |  |  |
| Pharmaceutical | 15 | 87\|90 | 88\|89 |  |  |  |  |  |
| \[16\] | \[91\|92\] |  |  |  |  |  |  |
| 17 | 93\|96 | 94\|95 |  |  |  |  |  |
| \[18\] | \[97\|98\] |  |  |  |  |  |  |
| 19 | 99\|102 | 100\|101 |  |  |  |  |  |
| Marginal Stars | 20 | 103\|116 | 104\|115 | 105\|114 | 106\|113 | 107\|112 | 108\|111 | \[109\|110\] |

Quire/Bifolio Breakdown for the Voynich Manuscript

(quires 16 and 18 are missing)

# Method

- 12 Comparisons made in this fashion are entire pages. As an example, for a conjoint score for 104\|115 (...)

33The first experiment explores how the text preserved on individual bifolia behaves within the constraints of each quire by using the LSA semantic spaces created to calculate each bifolium’s facing, confoliate, and conjoint scores 12 as well as the quire’s averages (keeping in mind that confoliate and conjoint scores are immutable). This will give us insight into how we might interpret the scores in the Voynich Manuscript and explore any notable differences or trends.

34The next experiment extends this to a bifolium-by-bifolium basis by calculating the confoliate scores for conjoint leaves (“1st leaf” and “2nd leaf”) - extending the comparison scores for the individual confoliate values in a bifolium to test their textual flow - as well as the interior-conjoint values. Again, we will compare the behavior of the values for the known text to the Voynich.

35The final experiment proposes a method to hypothesize the original sequence of bifolia in the balneological and the marginal-stars sections (Quires 13 and 20 respectively) of the Voynich Manuscript by producing a sequence that maximizes the similarity scores between sequential pages. These are contrasted with the current facing scores within the current nested quires. These two sections were selected because, as demonstrated in (Layfield & Davis, 2026), they have the highest topical coherence. The results for the Herbal section in (Layfield & Davis, 2026)suggested that each page is a distinct botanical topic (as also inferred from the illustrations, which change with each page); the cosmological and astrological sections are already singulions, not nested quires, as is the Rose foldout, and so additional testing was not warranted. The Pharmaceutical section contains fold-out leaves in each binion quire; therefore, it is not a good candidate for LSA analytics. That leaves the balneological section (ff. 75-84) and the marginal stars (ff. 103-116), the subjects of the following analysis.

36The next sections will present and analyze the results of these experiments. The final section will return to our original hypothesis that the Voynich was not meant to be bound in quires as it is today, but was instead meant to be a collection of un-nested and un-bound bifolia, including a discussion of the outcome of the re-ordering experiments.

# Results & Analysis

## Quire Experiments

37For the _Speculum_ manuscript, we used quires 1, 3 and 4 only (the text of quire 2 is error-prone, skipping several chapters, and thus was not appropriate for this experiment). For the _Aberdeen Bestiary,_ we used quires 2 through 12 (quire 1 is anomalous, with relatively little text on its pages and several blanks). We excluded singletons, as they lack a conjoint for comparison. For the Voynich Manuscript, we confined our analysis to quires 1-7 (herbal), 13 (biological/balneological), and 20 (marginal stars). The excluded quires are foldouts or are missing single leaves, or contain too little text to be analytically significant.

38Tables 6-8 below show the average confoliate (immutable), facing (mutable), and conjoint (immutable) similarity scores per quire for all three manuscripts. The confoliate scores include 1st-leaf and 2nd-leaf confoliate values.

Table 6

|     |     |     |     |
| --- | --- | --- | --- |
| **Quire** | **Confoliate Average** | **Facing Average** | **Conjoint Average** |
| 2 | 0.512 | 0.349 | 0.300 |
| 3 | 0.459 | 0.138 | 0.186 |
| 4 | 0.461 | 0.339 | 0.160 |
| 5 | 0.374 | 0.361 | 0.204 |
| 6 | 0.480 | 0.401 | 0.081 |
| 7 | 0.345 | 0.466 | 0.155 |
| 8 | 0.380 | 0.456 | 0.280 |
| 9 | 0.365 | 0.471 | 0.198 |
| 10 | 0.483 | 0.361 | 0.237 |
| 11 | 0.436 | 0.402 | 0.192 |
| 12 | 0.443 | 0.480 | 0.264 |

Quire Averages for Aberdeen Bestiary

Table 7

|     |     |     |     |
| --- | --- | --- | --- |
| **Quire** | **Confoliate Average** | **Facing Average** | **Conjoint Average** |
| 1 | 0.487 | 0.383 | 0.158 |
| 3 | 0.373 | 0.413 | 0.318 |
| 4 | 0.333 | 0.397 | 0.356 |

Quire Averages for Speculum

Table 8

|     |     |     |     |     |
| --- | --- | --- | --- | --- |
| **Section** | **Quire** | **Confoliate Average** | **Facing Average** | **Conjoint Average** |
| Herbal | 1 | 0.266 | 0.246 | 0.399 |
| 2 | 0.273 | 0.301 | 0.206 |
| 3 | 0.276 | 0.268 | 0.394 |
| 4 | 0.320 | 0.201 | 0.296 |
| 5 | 0.403 | 0.339 | 0.430 |
| 6 | 0.355 | 0.166 | 0.448 |
| 7 | 0.326 | 0.138 | 0.336 |
| Balneological | 13 | 0.530 | 0.460 | 0.603 |
| Marginal Stars | 20 | 0.568 | 0.438 | 0.600 |

Quire Averages for the Voynich Manuscript

- 13The outlier facing score in quire 3 of the Aberdeen Bestiary is explained by the drastic transition (...)

39Initial visual inspection of the data shows that the confoliate and facing averages are relatively close to one another for most quires in the _Aberdeen Bestiary_ and _Speculum_. 13 The conjoint averages, however, are almost always less than the facing and confoliate scores. This is exactly as expected: the confoliate and facing pages are by definition consecutive, while the conjoint pages are not (with the exception, as always, of the central bifolium). For the Voynich, however, it is the _facing_ score that tends to be the lowest of the three while the confoliate and conjoint scores are higher. In summary, the behaviour of the conjoint pages in the Voynich is quite different from that observed in the _Aberdeen Bestiary_ and the _Speculum_.

- 14The exceptions in the Aberdeen Bestiary can generally be explained by returning to the text: a dras (...)

40Another expected behaviour in the _Aberdeen Bestiary_ and the _Speculum_ manuscript is shown below: the conjoint pages in the central bifolium of each quire have a higher similarity score than the other conjoints in the quire. This is true for all of the analyzed _Speculum_ quires and for most of the quires from the Aberdeen Bestiary. 14 An example from the Aberdeen Bestiary is shown in Table 9, where the conjoint score for the central bifolium (28v\|29r) is significantly higher than the other conjoints in the quire. For the Voynich, this behaviour was observed only inconsistently, in three of nine quires for the Voynich text.

Table 9

|     |     |
| --- | --- |
| **Bifolio** | **Conjoint Score** |
| 25v \| 32r | 0.221 |
| 26v \| 31r | 0.022 |
| 27v \| 30r | 0.093 |
| 28v \| 29r | 0.479 |

Conjoint Scores for Quire 5 in Aberdeen Bestiary

41The overall average similarity scores for confoliate, facing, and conjoint scores are equally telling as seen in Table 10:

Table 10

|     |     |     |     |
| --- | --- | --- | --- |
| **Text** | **Overall Confoliate Average** | **Overall Facing Average** | **Overall Conjoint Average** |
| _Aberdeen Bestiary_ | 0.428 | 0.398 | 0.207 |
| _Speculum_ | 0.398 | 0.398 | 0.277 |
| Voynich | 0.383 | 0.298 | 0.433 |

Aberdeen Bestiary/Speculum/Voynich Overall Confoliate, Facing and Conjoint Average Scores

42As can be seen from the overall averages, confoliate and facing averages in the _Aberdeen Bestiary_ and _Speculum_ are aligned while the conjoint averages are considerably lower. The Voynich values tell a different story of confoliate averages aligned with the conjoint scores, leaving the facing averages behind. In other words, in the correctly-configured test manuscripts, the _mutable_ facing scores compare favorably to the _immutable_ confoliate scores, while in the Voynich it is the _mutable_ facing score that stands apart and the two _immutable_ scores that compare favorably. One possible explanation for this behaviour is that the bifolia in the Voynich manuscript are out of order.

- 15These tests are via the python functions shapiro and normaltest contained in the scipy library.

43We then carried out additional statistical tests as follows (this procedure applies to all statistics reported going forward): first, we checked the results sets to see whether or not they follow a normal (gaussian) distribution via the Shapiro-Wilk and the D’Agostino/Pearson’s test for normality. 15 The independent samples t-test (parametric) and the Mann Whitney test (non-parametric) are used to compare mean scores between two independent samples (e.g. Facing vs Conjoint). The first test is used when the score distribution satisfies the normality assumption, while the second test is used when the normality assumption is violated. The null hypothesis, _H_ _0_, specifies that the mean scores vary marginally between the two samples and is accepted if the p-value exceeds the 0.05 level of significance. The alternative hypothesis, _H_ _1_, specifies that the mean scores vary significantly between the two samples, and is accepted if the p-value is less than the 0.05 criterion. The p-value estimates how likely it would be to observe a pattern at least this strong if, in fact, there were no real relationships present. A smaller p-value means the observed result would be less likely to occur by chance alone. By convention, researchers often treat results as “statistically significant” when this probability falls below 0.05 (5%). In practical terms, this means that if there were truly no relationship, we would expect to see a pattern this strong fewer than 5 times out of 100 comparable studies. For our purposes, if the p-value score is below 0.05 we would consider the two datasets to _not_ behave in a similar fashion. The p-values that are reported in the following discussion are from the appropriate statistical tests (t-test or Mann Whitney test). Related samples refer to datasets where observations are connected, usually involving the same subjects measured twice (pre-test/post-test) or matched pairs. Independent samples refer to datasets where observations are recorded from different unrelated subjects. We consider observations for confoliate, facing, and conjoint as independent samples rather than related samples.

44The overall comparison scores between confoliate, facing, and conjoint values for the _Aberdeen Bestiary_ and _Speculum_ show normal-like tendencies (with the exception of the outlying conjoint score for the _Aberdeen Bestiary_) and we therefore give precedence to the t-test results except where the conjoint score for the non-normal distribution is used. Given the overall averages reported above in Table 10, it should come as no surprise that the statistical tests show that the confoliate and facing scores are likely to have come from the same, or a similar, distribution (that is, the confoliate scores and the facing scores more or less behave the same) as reported in Table 11 below. Given the _p_ value is > 0.05, the default _null hypothesis_ ( _H_ _0_, the two sample sets behave in a similar way) is accepted. A value of _p_ < 0.05 would indicate the two distributions do not behave in a similar way and the difference is statistically significant, therefore, the _null hypothesis_, _H_ _0_, would be rejected. However, the confoliate and facing scores are all different from the conjoint values in a statistically significant way with _p_ values well below 0.05, which tells us they come from a different distribution.

45For the Voynich semantic space, the normality tests indicated a normal-like distribution for all of the conjoint, confoliate, and facing scores, so we will use the t-test results. By inspecting Table 11 again, we see a different pattern emerge for the Voynich as compared with the known manuscripts, with significant values found for confoliate/facing and facing/conjoint scores. The confoliate/facing significance differs dramatically from the _Aberdeen Bestiary_ and _Speculum_ results. Significant values are displayed in **bold**.

Table 11

|     |     |     |     |
| --- | --- | --- | --- |
| **Text** | conf/facing | conf/conj | facing/conj |
| _Aberdeen Bestiary_ | 0.314 | **0.000** | **0.000** |
| _Speculum_ | 0.995 | **0.013** | **0.025** |
| Voynich | **0.005** | 0.168 | **0.000** |

Statistical Test Results for Overall Aberdeen Bestiary, Speculum and Voynich Quire Comparisons

## Bifolia Experiments

46The next experiment focuses on applying the methodology to individual bifolia instead of quires, considering each bifolium as an independent unit of four potentially-consecutive pages (first recto, first verso, second recto, second verso). Specifically, for each bifolium, we will calculate its first-leaf confoliate (first recto vs. first verso), conjoint (first verso vs. second recto), and second-leaf confoliate (second recto vs. second verso), values which are all immutable codicological properties of each bifolium. Unlike the previous set of tests, we are making the distinction between 1st confoliate and 2nd confoliate (the two leaves of a bifolium) to test the textual behaviour of these codicologically-related leaves. The average resulting values for the _Aberdeen Bestiary_, _Speculum,_ and the Voynich space are found in Table 12.

Table 12

|     |     |     |     |
| --- | --- | --- | --- |
| **Text** | **1st Confoliate Avg** | **Conjoint Avg** | **2nd Confoliate Avg** |
| _Aberdeen Bestiary_ | 0.418 | 0.207 | 0.438 |
| _Speculum_ | 0.422 | 0.277 | 0.373 |
| Voynich | 0.395 | 0.431 | 0.374 |

Overall Bifolum 1st Confoliate, Conjoint, and 2nd Confoliate Averages

47We again performed statistical tests between confoliate and conjoint values to identify any statistically-significant differences between them across the various manuscripts. The only collection of comparison scores that was not in a normal distribution is the set of conjoint scores for the _Aberdeen Bestiary_ and the 1st confoliate score for the Voynich. The results of these tests are reported below:

Table 13

|     |     |     |     |
| --- | --- | --- | --- |
| **Text** | 1st confol./ conjoint | 1st confol./ 2nd confol. | conjoint/<br>2nd confol. |
| _Aberdeen Bestiary_ | **0.000** | 0.632 | **0.000** |
| _Speculum_ | **0.008** | 0.359 | 0.108 |
| Voynich | 0.283 | 0.872 | 0.148 |

Statistical Test Results for Bifolium Ordering

48The only statistically significant results for the known texts are the 1st confoliate/conjoint values ( _Aberdeen Bestiary/Speculum_) and the conjoint/2nd confoliate values ( _Aberdeen Bestiary_). Those can be regarded as separate distributions of values (i.e. they behave differently). The _Speculum_ scores low (but not significantly so) on the conjoint/2nd confoliate values. In other words, the results for the Aberdeen Bestiary are extremely reliable, while interpreting the results for the _Speculum_(which is based on a smaller sample) requires more circumspection. For example, the conjoint score for _Speculum_ 39v\|46r was a surprisingly high .498, but a return to the text confirms that in spite of the distance between them, both pages happen to have some similar content, referring to the Last Judgement.

49As above, there is a clear difference between the two known texts and the Voynich space. The known texts have high values for both confoliates, with relatively low conjoint scores. By contrast, the average conjoint score for the Voynich is quite high and compares favorably to the respective confoliate values, as in the previous experiment. These experiments all reveal that the bifolia of the Voynich Manuscript behave in unexpected ways when compared to known texts.

## Bifolia Re-ordering Experiments

50The final experiment will investigate the effects of hypothetically re-sequencing the bifolia of the Voynich Manuscript by maximizing the mutable scores (that is, the transitions between sequential singulions), targeting quire 13 (five bifolia comprising the biological/balneological section) and quire 20 (six bifolia comprising the marginal stars section). To do this, we calculate every permutation of sequential, rather than nested, bifolia within each quire to identify the sequence with the highest average facing score at transitions between bifolia. This results in 120 permutations for the Balneology section and 720 permutations for the Stars section. The results can be found in Table 14. The current average facing score is calculated by analyzing the quire in its current form.

Table 14

|     |     |     |     |     |
| --- | --- | --- | --- | --- |
| Space | Section | Current Avg. Facing Score | Highest Facing Score for Sequential Bifolia | Resulting Singulion Sequence |
| Voynich | Balneology | 0.461 | 0.517 | 77\|82, 78\|81, 75\|84, 76\|83, 79\|80 |
| Voynich | Marginal Stars | 0.438 | 0.526 | 105\|114, 104\|115, 106\|113, 107\|112, 108\|111, 103\|116 |

Page Re-ordering Results

51By sequencing the singulions this way, the average facing scores are noticeably improved (by 12.1% and 20% respectively). In the balneological section, the visually-similar bifolia 78\|81 and 75\|84 appear in sequence - these are the two bifolia that illustrate groups of nude women bathing in interconnected pools. In the marginal stars re-ordering, the hypothetical singulion sequence starts with folio 105r, the only page in the section that begins with an oversize Voynichese glyph, likely confirming its role as the beginning of the section. The section also ends, as expected, with the originally blank folio 116v.

52For Quire 13, the second-highest score from the list of 120 possible scores, is noteworthy as well:

Table 15

|     |     |     |     |     |
| --- | --- | --- | --- | --- |
| Space | Section | Current Avg. Facing Score | Second-Highest Facing Score for Sequential Bifolia | Resulting Singulion Sequence |
| Voynich | Balneology | 0.461 | 0.494 | 76\|83, 77\|82, 79\|80, 75\|84, 78\|81 |

Quire 13, second-highest results

53This sequence begins with folio 76r, which has no illustrations but, like f. 105r, begins with an enlarged “initial” glyph as expected for the beginning of a section (Figure 4).

Figure 4

Enlarged glyphs in the upper left corner of folios 76r and 105r

(images courtesy of the Beinecke Rare Book & Manuscript Library)

54Like the top-scoring sequence, this option groups the visually-similar balneological bifolia 75\|84 and 78\|81 as a sequential pair, but places them at the end of the sequence instead of in the middle. This results in the remaining three bifolia, also visually similar to one another, forming an initial sequential triad. Because of these traits, this option may be worth considering as the “correct” sequence even though the average score improves by only 7.1%.

# Discussion

- 16The _Speculum_ conjoint and 2nd confoliate values (Table 12) are outliers (as explained above), but t (...)

55Revisiting our hypothesis, we can review the evidence. Our underlying approach is to try to ascertain if we can identify sequential and non-sequential pages and bifolia. In a known text, we would expect confoliate pages to score high, as they are immutably consecutive. The same should be true with the facing pages, as, again, they are meant to be read consecutively. Our experiments demonstrated that for known texts, the confoliate and facing scores behaved in a very similar way, with fairly high scores. This suggests that the confoliate pages and the facing pages are meant to be read in their current sequence. In contrast with this result, the confoliate/conjoint and facing/conjoint scores were significantly lower and statistically significant, indicating that the conjoint pages are not sequential (with the exception of the central conjoint, as always). The bifolia experiment - in which we calculate all of the static values for every bifolium - returns similar results; the 1st and 2nd confoliate scores correspond very nicely to one another, showing that they behave in a similar way. 16 This overall behaviour in the test manuscripts is exactly what we would expect and sets our baseline for comparison with the Voynich.

56The Voynich, however, tells us a different story. Looking back at Tables 10 and 11, we see that the Voynich behaves quite differently from the known texts. The confoliate/conjoint scores behave in a similar way, with no significant difference between them. This implies that the score distribution for each behaves in a similar fashion. Because we know that confoliate pages are by definition meant to be read in sequence, this would strongly imply that the conjoint pages are as well. This observation directly contradicts the expectations of the current nested quire structure. The statistically-significant difference between confoliate/facing scores adds additional evidence to support this conclusion, implying that confoliate/facing pages were likely not meant to be read in their current order. The bifolia experiment, as reported in Tables 12 and 13, also reveals that the bifolia of the Voynich Manuscript display different behaviour as compared to the known texts. The behaviour of 1st confoliate, 2nd confoliate, and the conjoint scores are similar, which, again, suggests that each bifolium is meant to be read as a four-page sequence. Given our findings, there is very strong evidence that the Voynich was not meant to be nested and bound in quires at all, but was meant to be a collection of loose singulions. The Voynich differs in that facing/confoliate scores are low (and significant) and conjoint/confoliate scores are high, as are the confoliate scores - which suggests they are meant to be read as single bifolia of four consecutive pages. It should be noted, however, there are other explanations for this behaviour, that is, high conjoint scores and low facing scores. It could be by chance. The Voynich could have a limited vocabulary that makes repetitive text more common, resulting in higher scores (although this would not explain the low facing scores). Or it could have to do with other examples of formulaic or repetitive text, although this, too, would not explain the low facing scores. These alternative explanations seem unlikely, especially given the low-facing-scores and high-conjoint-scores behaviour of the text, but it is certainly possible that there may be other, unknown, explanations. The evidence, however, strongly supports the singulion hypothesis. Research Question 1 asks: “Is there evidence that the Voynich Manuscript is misbound and it is intended to be a loose collection of singulion folios?” The answer is “Yes.”

57The page re-ordering experiment demonstrates a possible way to suggest the correct sequence of singulions. While it is certainly possible that there is in fact no “correct” sequence of singulions (especially in the botanical section), our results for the balneological and marginal-stars sections demonstrate that we could present a singulion sequence (via an exhaustive search of the permutation space) that would improve the average facing score. These hypothetical singulion sequences are supported by graphic and physical evidence, such as the initial glyphs on folios 76r and 105r. This answers Research Question 2: “If we treat the manuscript as a collection of singulion bifolia, is there any way to infer their original sequence?” Here, too, the answer may be “Yes.” We qualify the response with “may be” because while we presented a method to reorder the pages by comparing the individual bifolium facing scores against the facing scores contained within the current quire, until and unless we can actually read the manuscript, we cannot know for sure that this hypothesis is correct. Even so, the proposed singulion structure for the Voynich Manuscript opens up additional avenues of investigation for future research.

# Conclusions

58The Voynich Manuscript has proven an inscrutable puzzle that has frustrated linguists, cryptologists, and bibliographers for centuries. The novel idea expressed in this paper that 1) the entire manuscript is bound out of order and 2) it was originally intended to be read as a series of sequential singulions rather than nested quires, may partially explain this lack of success. A book whose pages are out of order is almost certainly more difficult to read. It is our hope that linguists and cryptologists will revisit past work in the light of this hypothesis, ushering in a new era of Voynich Studies.

## Bibliography

Altszyler, E., M. Sigman, S. Ribeiro, D. Fernández Sleak (2017). Comparative study of LSA vs Word2Vec embeddings in small corpora: a case study in dreams database. arXiv:1610.01520.

Claire L. B. and L. Lindemann (2021), “The Linguistics of the Voynich Manuscript,” _Annual Review of Linguistics_ 7, 285-308. https://doi.org/10.1146/annurev-linguistics-011619-030613

DOI : 10.1146/annurev-linguistics-011619-030613

Currier, P. (1976). “Some Important New Statistical Findings,” in _New Research on the Voynich Manuscript - Proceedings of a Seminar, 30 November 1976_ 20-26 (unpublished typescript, <https://media.defense.gov/2021/Jul/13/2002761428/-1/-1/0/PROCEEDINGS-OF-A-SEMINAR-30-NOVEMBER-1976.PDF>.

Davis, L. F. (2020), “How Many Glyphs and How Many Scribes? Digital Paleography and the Voynich Manuscript,” _Manuscript Studies: A Journal of the Schoenberg Institute for Manuscript Studies_, University of Pennsylvania Press, Volume 5, Number 1, 164-180

DOI : 10.1353/mns.2020.0011

Davis, L. F. (2022), “Voynich Paleography,” Keynote address presented at the 2022 Voynich MS Conference, Malta.

Deerwester, S., S. Dumais, G. Furnas, T. Landauer, and R. Harshman (1990). "Indexing by Latent Semantic Analysis." _Journal of the American Society for Information Science_ _,_ Volume 41, Number 6 _,_ 391-407.

DOI : 10.1002/(SICI)1097-4571(199009)41:6<391::AID-ASI1>3.0.CO;2-91097-4571(199009)41:6%3C391::AID-ASI1%3E3.0.CO;2-9)

Dos Santos, J. C. A. and Favero, E. L. 2015. “Practical use of a latent semantic analysis (LSA) model for automatic evaluation of written answers”. _Journal of the Brazilian Computer Society._ 21:21.

D'Imperio, M. E. (1978), _The Voynich Manuscript - an elegant enigma._ Aegean Park Press.

Foltz, P., W. Kintsch, and T. Landauer. 1998\. "The Measurement of Textual Coherence With Latent Semantic Analysis." _Discourse Processes_ 285-307.

DOI : 10.1080/01638539809545029

Layfield, C. and L. F. Davis (2026) “The Application of Latent Semantic Analysis to the Voynich Manuscript”, _Digital_ _Humanities Quarterly_, Volume 20, Number 1, 1-28.

DOI : 10.63744/2ezxpskcezq4

Pelling, N. (2006), _Curse of the Voynich_. Compelling Press.

Zandbergen, R. (2020). "IVTFF - Intermediate Voynich MS Transliteration File Format - File Format 1.7." 04 10.

Zyats, P. (2016), “Physical Findings” in Raymond Clemens, ed., _The Voynich Manuscript_, 23-38.

## Appendix

Appendix 1

The Appendix further explores the LSA methodology, presenting justification for the selection of the dimensional reduction value of _k_. We will also address a circular self-referential issue in that semantic spaces, and the testing/experimentation use the same datasets. This was originally addressed in (Layfield & Davis, 2026) and is largely reproduced here for convenience with the context updated for the work done in this paper.

Selection of _k_

The dimensional reduction step in LSA involves a selection of the number of dimensions to use from the SVD decomposition. This is a tricky choice and much of the literature (especially in the context of Information Retrieval (IR)) suggests you pick a _k_ that gives you the best results (for a typical train/test split for an IR problem this is straightforward). As we do not know the contents of the Voynich, such a strategy would be impossible. Instead, we use three heuristics to approximate a good value for _k_ by calculating what might be a good lower, mid and upper bound selection of values. We first calculate a coherence score, which is the average similarity of adjacent documents in the _D_ _T_ matrix. Next, we shuffle the order of the documents in _D_ _T_ and make the same calculation (random) and do this 10 times taking the average. This is similar to the coherence experiment in (Layfield and Davis, 2026). We then use three different techniques to approximate _k_.

1\. Noise separation – Compare the baseline coherence for a dimension with the random baseline. Select the _k_ with the largest difference (indicates a strong semantic pattern). This would act as the lower bound for _k,_ as typically the difference is largest the smaller the dimension (assuming the text has any coherence).

2\. Elbow detection – Find the point of diminishing returns in the coherence scores. This is often indicated by the “elbow” of the coherence scores over the range of k. The similarity scores at this point begin to taper off. This is typically the default value of _k_ as it should be larger than the Noise separation value and smaller than the Slope stabilization value.

3\. Slope stabilization – Identify when the coherence values begin to flatten out. As the dimension increases, usually the scores decrease. When the scores flatten out, additional dimensions contribute very little. This is typically the upper bound for a reasonable _k_.

We ran these heuristics over a _k_ range of \[25, 200\]. We did this for all datasets used, TF, TF-IDF and Log-Entropy in weighting methods, as well as document sizes of 20, 30 and 40 from our work in (Layfield & Davis, 2026). The range of values for the noise separation methods was \[25, 30\], for elbow detection it was \[65, 90\] and for the slope stabilization method it was \[115, 160\]. The semantic spaces used in this paper are virtually identical to those used in (Layfield & Davis, 2026), so we, again, ascertain that a reasonable range for _k_ is in the range of 65-90. As we used a value of 75 in our previous work, we elected to employ it again as the value of _k_ used here.

Circular Self-Referential issue

It is worth noting that each semantic space is trained on its own document and comparisons/experimentation are conducted within that semantic space. This can be viewed as a _circular_ relationship or, perhaps better stated, self-contained distributional modelling (in the sense the training data is what we are working on) and can be potentially viewed as problematic. Our experiments are _not_ testing _generalization_ (an issue with over-fitting), but internal-structure instead. The goal of our work is to characterise internal coherence and discourse structure rather than predictive performance or generalization. There is also some precedence for the usage of a generated semantic space and experimentation on the same space with the data it was trained on. (Dos Santos & Favero, 2015) built an LSA semantic space from a set of student answers to exam questions. They evaluated the performance of this on the same dataset (comparing human-assigned scores to computer-generated scores) and reported an 85% agreement with human scoring. (Altszyler _et al._, 2017) applied LSA using a semantic space made up of dream reports analysing usage patterns of words between dreams and waking life (the analysis making use of the same semantic space data). They also compared the results with Word2Vec, deducing that with a smaller corpus, Word2Vec becomes less effective compared to LSA. In addition, the paper Foltz, _et al_ (1998) literally uses a semantic space trained on a dataset and then performs discourse segmentation on this space using the same dataset (no external data was used for training).

Appendix 2

Figure A1

Stop Words for _Speculum (Latin)_

Figure A2

Stop Words for _Aberdeen Bestiary_ (Latin)

Figure A3

Stop Words for the Voynich Manuscript

## Notes

1 The entire manuscript may be viewed here: https://beinecke.library.yale.edu/collections/highlights/voynich-manuscript.

2 E.g. Bowern and Lindemann 2021.

3 In what follows, conjoint bifolia are indicated by two folio numbers separated by a vertical line, as in 10\|15, two leaves that are conjoint (i.e. attached at the gutter) but not currently consecutive.

4 There is also one page - 115r - on which two scribes (2 and 3) collaborated.

5 In the center of a quire, the facing pages are also conjoint.

6 Aberdeen University Library MS 24 <https://www.abdn.ac.uk/bestiary/>

7 Harvard University (Cambridge, Massachusetts, United States of America), Houghton Library MS Lat 121<https://iiif.lib.harvard.edu/manifests/view/drs:16870940$1i>

8 F. 116v is not part of the primary text and will not be considered here.

9 The transliteration files can be found here: https://www.voynich.nu/transcr.html

10 We are using TF-IDF as we found it useful in our previous work on LSA on the Voynich (and other texts). We also experimented with TF and Log-Entropy in our earlier experiments (Layfield & Davis, 2026).

11 A cosine value has the range \[-1.0, 1.0\]

12 Comparisons made in this fashion are entire pages. As an example, for a conjoint score for 104\|115 in the Voynich we would fold in (generate new columns in the space of _D_ _T_) using the entire page of text from 104v and 115r (sans stop words) and calculate the cosine score between them.

13 The outlier facing score in quire 3 of the Aberdeen Bestiary is explained by the drastic transitions within topics in that quire.

14 The exceptions in the Aberdeen Bestiary can generally be explained by returning to the text: a drastic change in topic for unexpectedly-low scores and surprising similarities in vocabulary between apparently-distinct topics for unexpectedly-high scores. For example, conjoint folios 8v (concerning tigers) and 11r (concerning elephants and ibexes) should have a relatively-low similarity score, but instead, the score is surprisingly high. Reference to the text explains the anomaly: because both entries focus on running and evading hunters, their vocabulary shows a higher-than-expected similarity.

15 These tests are via the python functions shapiro and normaltest contained in the scipy library.

16 The _Speculum_ conjoint and 2nd confoliate values (Table 12) are outliers (as explained above), but the overall trend in the averages suggest a difference between the conjoint and 2nd confoliate (although not statistically significant).


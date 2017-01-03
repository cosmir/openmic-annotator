---
layout: page
title: Task 2
---

# Task 2: Retrieval

In this task we consider a user with a corpus of audio music files, who wants a system to retrieve the files in which a certain instrument is played. This is the case for instance of amateur players who want to practice some particular instrument.

## Format

The input to the system is a query instrument and a corpus of audio music files. The output is a ranked list of at most $M=1000$ files where the query instrument is played.

[TBD]

## Evaluation

Several evaluation measures will be used to score a system output for a query instrument.
Let $q$ be the query instrument, let $B(q)=\langle b_1,\dots,b_m \rangle$ be the list of excerpts retrieved by the system for that instrument, and let $A(e)=\\{a_1,\dots,a_n \\}$ be the set of instruments annotated for excerpt $e$. An excerpt $b_i$ will thus be considered relevant for instrument $q$ if $q \in A(b_i)$. In addition, let $1[x]$ be an indicator function that evaluates to $1$ if $x$ is true and $0$ otherwise.

The following measures will be used to score a system output for a query instrument:

- **Reciprocal Rank** evaluates the (inverse of the) effort required from the user to find the first relevant excerpt retrieved:

  $$RR=\frac{1}{\min_{i}{\{i : q \in A(b_i)\}}}$$

- **Precision at k** evaluates the ability of the system to retrieve relevant excerpts among the top $k$ retrieved:

  $$P@k=\frac{1}{ min(k,n) }\sum_{i=1}^k{1[q \in A(b_i)]}$$

  We will evaluate with cutoffs $k=5,10,15,20,50,100$.

- **Average Precision** evaluates the ability of the system to retrieve all relevant excerpts and at the top of the results list:

  $$AP=\frac{1}{ min(M,n) }\sum_{i=1}^m{1[q \in A(b_i)]\cdot P@i}$$

For each measure, systems will be ranked by mean score over all instruments in the taxonomy.

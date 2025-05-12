<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron">
  <title>Argument Map Business Rules</title>

  <!-- Namespace declaration for clarity -->
  <ns prefix="arg" uri="http://example.com/argument_map"/>

  <!-- Pattern for validating statement references in relationships -->
  <pattern>
    <rule context="//arg:support | //arg:oppose">
      <assert test="@from = //arg:premise/@id or @from = //arg:conclusion/@id or @from = //arg:rebuttal/@id or @from = //arg:counter_conclusion/@id">
        The 'from' attribute must reference an existing statement ID (premise, conclusion, rebuttal, or counter_conclusion).
      </assert>
      <assert test="@to = //arg:premise/@id or @to = //arg:conclusion/@id or @to = //arg:rebuttal/@id or @to = //arg:counter_conclusion/@id">
        The 'to' attribute must reference an existing statement ID (premise, conclusion, rebuttal, or counter_conclusion).
      </assert>
    </rule>
  </pattern>

  <!-- Pattern for validating evidence references -->
  <pattern>
    <rule context="//arg:evidence/arg:item">
      <assert test="@for = //arg:premise/@id or @for = //arg:conclusion/@id or @for = //arg:rebuttal/@id or @for = //arg:counter_conclusion/@id">
        The 'for' attribute in evidence items must reference an existing statement ID (premise, conclusion, rebuttal, or counter_conclusion).
      </assert>
    </rule>
  </pattern>

  <!-- Pattern for validating linked premises with group_id -->
  <pattern>
    <rule context="arg:support[@group_id]">
      <assert test="every $g in ../arg:support[@group_id = current()/@group_id] satisfies $g/@to = current()/@to">
        All supports with the same group_id must target the same conclusion.
      </assert>
    </rule>
  </pattern>

  <!-- Additional pattern to ensure unique IDs for statements -->
  <pattern>
    <rule context="//arg:premise | //arg:conclusion | //arg:rebuttal | //arg:counter_conclusion">
      <assert test="count(//@id[. = current()/@id]) = 1">
        The ID attribute '<value-of select="@id"/>' must be unique across all statements.
      </assert>
    </rule>
  </pattern>

  <!-- Pattern to ensure unique IDs for evidence items -->
  <pattern>
    <rule context="//arg:evidence/arg:item">
      <assert test="count(//arg:evidence/arg:item/@id[. = current()/@id]) = 1">
        The ID attribute '<value-of select="@id"/>' for evidence items must be unique.
      </assert>
    </rule>
  </pattern>

  <!-- Pattern to prevent self-referencing relationships -->
  <pattern>
    <rule context="//arg:support | //arg:oppose">
      <assert test="@from != @to">
        The 'from' and 'to' attributes must not reference the same statement ID.
      </assert>
    </rule>
  </pattern>

</schema>
// Create a blank query called fnLoadCsv. DataFolder is a text parameter.
(fileName as text, columnTypes as list) as table =>
let
    Source = Csv.Document(
        File.Contents(DataFolder & "\" & fileName),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    EmptyAsNull = Table.TransformColumns(Headers,
        List.Transform(Table.ColumnNames(Headers),
            (columnName) => {columnName, (value) => if value = "" then null else value})),
    Typed = Table.TransformColumnTypes(EmptyAsNull, columnTypes, "en-US")
in
    Typed


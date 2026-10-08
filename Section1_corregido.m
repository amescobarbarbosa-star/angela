section Section1;

shared Period = let
    Source = Excel.CurrentWorkbook(){[Name="LASTDAY"]}[Content],
    #"Changed Type" = Table.TransformColumnTypes(Source,{{"Period", Int64.Type}, {"Last_Day", type datetime}}),
    #"Changed Type1" = Table.TransformColumnTypes(#"Changed Type",{{"Last_Day", type date}})
in
    #"Changed Type1";

shared HOLIDAYS = let
    Source = Excel.CurrentWorkbook(){[Name="HOLIDAYS"]}[Content],
    #"Changed Type" = Table.TransformColumnTypes(Source,{{"Period", Int64.Type}, {"Date", type datetime}, {"Type", type text}}),
    #"Changed Type1" = Table.TransformColumnTypes(#"Changed Type",{{"Date", type date}})
in
    #"Changed Type1";

shared USERS = let
    Source = Excel.CurrentWorkbook(){[Name="USERS"]}[Content],
    #"Changed Type" = Table.TransformColumnTypes(Source,{{"Auth_Users", type text}, {"Department", type text}, {"Reviewer", type text}}),
    #"Filtered Rows" = Table.SelectRows(#"Changed Type", each [Auth_Users] <> null and [Auth_Users] <> "")
in
    #"Filtered Rows";

shared #"SODA VALUE" = let
    Source = Excel.CurrentWorkbook(){[Name="VALUE6"]}[Content],
    #"Changed Type" = Table.TransformColumnTypes(Source,{{"Period", Int64.Type}, {"Value", Int64.Type}}),
    #"Filtered Rows" = Table.SelectRows(#"Changed Type", each true),
    #"Tipo cambiado" = Table.TransformColumnTypes(#"Filtered Rows",{{"Period", Int64.Type}, {"Value", type number}})
in
    #"Tipo cambiado";

shared #"Doc Type" = let
    Source = Excel.CurrentWorkbook(){[Name="VALUE"]}[Content],
    #"Changed Type" = Table.TransformColumnTypes(Source,{{"Doc. Type", type text}, {"Description", type text}})
in
    #"Changed Type";

shared Download = let
    Source = Excel.Workbook(File.Contents("\\dss-ib-dfs-228\SSC Valladolid\7.- Governances & Audits\Control GFPM6\C17\FY 2027\AP08\LUCCA\Datos control C17 Lucca AP08.XLSX"), null, true),
    Sheet1_Sheet = Source{[Item="Sheet1",Kind="Sheet"]}[Data],
    #"Encabezados promovidos1" = Table.PromoteHeaders(Sheet1_Sheet, [PromoteAllScalars=true]),
    #"Filas vacias quitadas" = Table.SelectRows(#"Encabezados promovidos1", each [Document Number] <> null and [User Name] <> null),
    #"Tipo cambiado" = Table.TransformColumnTypes(#"Filas vacias quitadas",{{"Posting period", Int64.Type}, {"User Name", type text}, {"Company Code", type text}, {"Document Number", Int64.Type}, {"Document Date", type date}, {"Posting Date", type date}, {"Entry Date", type date}, {"Business Area", type any}, {"Document Type", type text}, {"Account", Int64.Type}, {"Amount in foreign cur.", type number}, {"Currency", type text}, {"Account Type", type text}})
in
    #"Tipo cambiado";

shared DB = let
    Source = Table.NestedJoin(Download, {"User Name"}, USERS, {"Auth_Users"}, "USERS", JoinKind.LeftOuter),
    #"Expanded USERS" = Table.ExpandTableColumn(Source, "USERS", {"Department", "Reviewer", "SSC"}, {"USERS.Department", "USERS.Reviewer", "USERS.SSC"}),
    #"Merged Queries" = Table.NestedJoin(#"Expanded USERS", {"Posting period"}, Period, {"Period"}, "Period", JoinKind.LeftOuter),
    #"Expanded Period" = Table.ExpandTableColumn(#"Merged Queries", "Period", {"Last_Day"}, {"Period.Last_Day"}),
    #"Added Custom" = Table.AddColumn(#"Expanded Period", "F.1", each if [Entry Date] <> null and [Period.Last_Day] <> null and [Entry Date] > [Period.Last_Day] then 1 else 0),
    #"Merged Queries1" = Table.NestedJoin(#"Added Custom", {"Entry Date"}, HOLIDAYS, {"Date"}, "HOLIDAYS", JoinKind.LeftOuter),
    #"Expanded HOLIDAYS" = Table.ExpandTableColumn(#"Merged Queries1", "HOLIDAYS", {"Type"}, {"HOLIDAYS.Type"}),
    #"Added Custom1" = Table.AddColumn(#"Expanded HOLIDAYS", "F.2", each if [HOLIDAYS.Type] = null then 0 else 1),
    #"Added Custom2" = Table.AddColumn(#"Added Custom1", "F.3", each if [USERS.Department] = "R2R" then 0 else 1),
    #"Merged Queries2" = Table.NestedJoin(#"Added Custom2", {"Posting period"}, #"SODA VALUE", {"Period"}, "SODA VALUE", JoinKind.LeftOuter),
    #"Expanded SODA VALUE" = Table.ExpandTableColumn(#"Merged Queries2", "SODA VALUE", {"Value"}, {"SODA VALUE.Value"}),
    #"Added Custom3" = Table.AddColumn(#"Expanded SODA VALUE", "F.4", each if [SODA VALUE.Value] <> null and [#"Amount in foreign cur."] <> null and Number.Abs([#"Amount in foreign cur."]) > [SODA VALUE.Value] then 1 else 0),
    #"Added Custom4" = Table.AddColumn(#"Added Custom3", "F.5", each if [Account Type] = "D" or [Account Type] = "K" then 1 else 0),
    #"Merged Queries3" = Table.NestedJoin(#"Added Custom4", {"Document Number", "Business Area", "Company Code"}, F6, {"Document Number", "Business Area", "Company Code"}, "F6", JoinKind.LeftOuter),
    #"Expanded F6" = Table.ExpandTableColumn(#"Merged Queries3", "F6", {"F.6"}, {"F6.F.6"}),
    #"Merged Queries4" = Table.NestedJoin(#"Expanded F6", {"Account"}, #"Plan de Cuentas", {"G/L Account"}, "Plan de Cuentas", JoinKind.LeftOuter),
    #"Expanded Plan de Cuentas" = Table.ExpandTableColumn(#"Merged Queries4", "Plan de Cuentas", {"Unmapped"}, {"Plan de Cuentas.Unmapped"}),
    #"Added Conditional Column" = Table.AddColumn(#"Expanded Plan de Cuentas", "F7", each if [F.5] = 1 then 0 else (if [Plan de Cuentas.Unmapped] = null then 1 else [Plan de Cuentas.Unmapped])),
    #"Columna condicional agregada" = Table.AddColumn(#"Added Conditional Column", "F.7", each if [F7] = 0 then 0 else 1),
    #"Merged Queries5" = Table.NestedJoin(#"Columna condicional agregada", {"Company Code", "Document Number", "Account"}, E1, {"Company Code", "Document Number", "Account"}, "E1", JoinKind.LeftOuter),
    #"Expanded E2" = Table.ExpandTableColumn(#"Merged Queries5", "E1", {"Redondeo"}, {"E1.Redondeo"}),
    #"Added Conditional Column2" = Table.AddColumn(#"Expanded E2", "E2", each if [Document Type] = "D1" then 0 else 1),
    #"Added Custom6" = Table.AddColumn(#"Added Conditional Column2", "Ftot", each [F.1]+[F.2]+[F.3]+[F.4]+[F.5]+[F6.F.6]+[F.7]),
    #"Consultas combinadas1" = Table.NestedJoin(#"Added Custom6", {"Account"}, #"Account Type", {"Loc Account"}, "Account Type.1", JoinKind.LeftOuter),
    #"Se expandió Account Type.1" = Table.ExpandTableColumn(#"Consultas combinadas1", "Account Type.1", {"Group"}, {"Account Type.1.Group"}),
    #"Valor reemplazado" = Table.ReplaceValue(#"Se expandió Account Type.1",null,0,Replacer.ReplaceValue,{"Account Type.1.Group"}),
    #"Consultas combinadas2" = Table.NestedJoin(#"Valor reemplazado", {"Company Code", "Document Number", "Account Type.1.Group"}, E3, {"Company Code", "Document Number", "Account Type.1.Group"}, "E3", JoinKind.LeftOuter),
    #"Se expandió E3" = Table.ExpandTableColumn(#"Consultas combinadas2", "E3", {"E.3"}, {"E3.E.3"}),
    #"Columnas con nombre cambiado" = Table.RenameColumns(#"Se expandió E3",{{"E3.E.3", "E.3"}, {"USERS.Department", "Department"}, {"USERS.Reviewer", "Reviewer"}, {"USERS.SSC", "SSC"}, {"Account Type.1.Group", "Group Account Type"}, {"E1.Redondeo", "E.1"}, {"E2", "E.2"}, {"F6.F.6", "F.6"}}),
    #"Columnas quitadas" = Table.RemoveColumns(#"Columnas con nombre cambiado",{"Period.Last_Day", "HOLIDAYS.Type", "SODA VALUE.Value", "Plan de Cuentas.Unmapped", "F7"}),
    #"Columnas reordenadas" = Table.ReorderColumns(#"Columnas quitadas",{"Posting period", "User Name", "Company Code", "Document Number", "Document Date", "Posting Date", "Entry Date", "Business Area", "Document Type", "Account", "Amount in foreign cur.", "Currency", "Account Type", "Group Account Type", "Department", "Reviewer", "SSC", "F.1", "F.2", "F.3", "F.4", "F.5", "F.6", "F.7", "Ftot", "E.1", "E.2", "E.3"}),
    #"Tipo cambiado" = Table.TransformColumnTypes(#"Columnas reordenadas",{{"Document Date", type date}, {"Posting Date", type date}, {"Entry Date", type date}, {"Account", Int64.Type}})
in
    #"Tipo cambiado";

shared F6 = let
    Origen = Download,
    #"Filas agrupadas" = Table.Group(Origen, {"Company Code", "Document Number", "Business Area"}, {{"F6", each List.Sum([#"Amount in foreign cur."]), type number}}),
    Redondeado = Table.TransformColumns(#"Filas agrupadas",{{"F6", each Number.Round(_, 2), type number}}),
    #"Columna condicional agregada" = Table.AddColumn(Redondeado, "F.6", each if [F6] = 0 then 0 else 1)
in
    #"Columna condicional agregada";

shared E1 = let
    Origen = Download,
    #"Filas agrupadas" = Table.Group(Origen, {"Company Code", "Document Number", "Account"}, {{"E1", each List.Sum([#"Amount in foreign cur."]), type number}}),
    Redondeado = Table.TransformColumns(#"Filas agrupadas",{{"E1", each Number.Round(_, 2), type number}}),
    #"Columna condicional agregada" = Table.AddColumn(Redondeado, "Redondeo", each if [E1] = 0 then 0 else 1)
in
    #"Columna condicional agregada";

shared #"Plan de Cuentas" = let
    Source = Excel.CurrentWorkbook(){[Name="Table6"]}[Content],
    #"Columnas necesarias" = Table.SelectColumns(Source,{"G/L Account", "Group Account", "Unmapped"}),
    #"Changed Type" = Table.TransformColumnTypes(#"Columnas necesarias",{{"G/L Account", Int64.Type}, {"Group Account", type text}, {"Unmapped", type number}}),
    #"Sin vacios" = Table.SelectRows(#"Changed Type", each [#"G/L Account"] <> null),
    #"Cuentas unicas" = Table.Distinct(#"Sin vacios", {"G/L Account"})
in
    #"Cuentas unicas";

shared #"Account Type" = let
    Origen = Excel.CurrentWorkbook(){[Name="LocalAccount"]}[Content],
    #"Tipo cambiado" = Table.TransformColumnTypes(Origen,{{"Loc Account", Int64.Type}, {"Group", Int64.Type}})
in
    #"Tipo cambiado";

shared #"User Check" = let
    Source = Table.NestedJoin(Download, {"User Name"}, USERS, {"Auth_Users"}, "USERS", JoinKind.LeftOuter),
    #"Expanded USERS" = Table.ExpandTableColumn(Source, "USERS", {"Auth_Users"}, {"USERS.Auth_Users"}),
    #"Filas filtradas" = Table.SelectRows(#"Expanded USERS", each [USERS.Auth_Users] = null),
    #"Duplicados quitados" = Table.Distinct(#"Filas filtradas", {"User Name"}),
    #"Otras columnas quitadas" = Table.SelectColumns(#"Duplicados quitados",{"User Name"})
in
    #"Otras columnas quitadas";

shared #"Doc Type Check" = let
    Source = Table.NestedJoin(Download, {"Document Type"}, #"Doc Type", {"Doc. Type"}, "Doc Type", JoinKind.LeftOuter),
    #"Expanded Doc Type" = Table.ExpandTableColumn(Source, "Doc Type", {"Doc. Type"}, {"Doc Type.Doc. Type"}),
    #"Filtered Rows" = Table.SelectRows(#"Expanded Doc Type", each ([Doc Type.Doc. Type] = null)),
    #"Otras columnas quitadas" = Table.SelectColumns(#"Filtered Rows",{"Document Type"}),
    #"Duplicados quitados" = Table.Distinct(#"Otras columnas quitadas")
in
    #"Duplicados quitados";

shared #"Check #N/D" = let
    Origen = DB,
    #"Columna condicional agregada" = Table.AddColumn(Origen, "Check #N/D", each if [F.1] = null then [Document Number] else if [F.2] = null then [Document Number] else if [F.3] = null then [Document Number] else if [F.4] = null then [Document Number] else if [F.5] = null then [Document Number] else if [F.6] = null then [Document Number] else if [F.7] = null then [Document Number] else if [E.1] = null then [Document Number] else if [E.2] = null then [Document Number] else if [E.3] = null then [Document Number] else "No errors"),
    #"Filas filtradas" = Table.SelectRows(#"Columna condicional agregada", each [#"Check #N/D"] <> "No errors"),
    #"Otras columnas quitadas" = Table.SelectColumns(#"Filas filtradas",{"Check #N/D"})
in
    #"Otras columnas quitadas";

shared #"Check Cuentas" = let
    Origen = DB,
    #"Consultas combinadas" = Table.NestedJoin(Origen, {"Account"}, #"Plan de Cuentas", {"G/L Account"}, "Plan de Cuentas", JoinKind.LeftOuter),
    #"Se expandió Plan de Cuentas" = Table.ExpandTableColumn(#"Consultas combinadas", "Plan de Cuentas", {"G/L Account"}, {"Plan de Cuentas.G/L Account"}),
    #"Filas filtradas" = Table.SelectRows(#"Se expandió Plan de Cuentas", each ([Account Type] = "S")),
    #"Filas filtradas1" = Table.SelectRows(#"Filas filtradas", each [#"Plan de Cuentas.G/L Account"] = null),
    #"Otras columnas quitadas" = Table.SelectColumns(#"Filas filtradas1",{"Account"})
in
    #"Otras columnas quitadas";

shared #"Check Doc Duplicado" = let
    Origen = Random,
    #"Consultas combinadas" = Table.NestedJoin(Origen, {"Document Number"}, #"3 OR MORE", {"Document Number"}, "3 OR MORE", JoinKind.LeftOuter),
    #"Se expandió 3 OR MORE" = Table.ExpandTableColumn(#"Consultas combinadas", "3 OR MORE", {"Document Number"}, {"Document Number.1"}),
    #"Tipo cambiado" = Table.TransformColumnTypes(#"Se expandió 3 OR MORE",{{"Document Number.1", type text}}),
    #"Valor reemplazado" = Table.ReplaceValue(#"Tipo cambiado",null,"No Duplicado",Replacer.ReplaceValue,{"Document Number.1"}),
    #"Columnas quitadas" = Table.RemoveColumns(#"Valor reemplazado",{"Department", "Reviewer", "Document Number", "Company Code"}),
    #"Filas ordenadas" = Table.Sort(#"Columnas quitadas",{{"User Name", Order.Ascending}})
in
    #"Filas ordenadas";

shared E3 = let
    Source = Download,
    #"Consultas combinadas" = Table.NestedJoin(Source, {"Account"}, #"Account Type", {"Loc Account"}, "Account Type.1", JoinKind.LeftOuter),
    #"Se expandió Account Type.1" = Table.ExpandTableColumn(#"Consultas combinadas", "Account Type.1", {"Group"}, {"Account Type.1.Group"}),
    #"Valor reemplazado" = Table.ReplaceValue(#"Se expandió Account Type.1",null,0,Replacer.ReplaceValue,{"Account Type.1.Group"}),
    #"Filas agrupadas" = Table.Group(#"Valor reemplazado", {"Company Code", "Document Number", "Account Type.1.Group"}, {{"E3", each List.Sum([#"Amount in foreign cur."]), type nullable number}}),
    Redondeado = Table.TransformColumns(#"Filas agrupadas",{{"E3", each Number.Round(_, 2), type number}}),
    #"Columna condicional agregada" = Table.AddColumn(Redondeado, "E.3", each if [E3] = 0 then 0 else 1)
in
    #"Columna condicional agregada";

shared #"3 OR MORE" = let
    Origen = DB,
    #"Filas filtradas" = Table.SelectRows(Origen, each [E.1] = 1),
    #"Filas filtradas1" = Table.SelectRows(#"Filas filtradas", each [E.2] = 1),
    #"Filas filtradas3" = Table.SelectRows(#"Filas filtradas1", each [SSC] = "Yes"),
    #"Filas filtradas2" = Table.SelectRows(#"Filas filtradas3", each [Ftot] >= 3),
    #"Columnas quitadas" = Table.RemoveColumns(#"Filas filtradas2",{"Posting period", "Document Date", "Posting Date", "Entry Date", "Business Area", "Document Type", "Account", "Amount in foreign cur.", "Currency", "Account Type", "SSC", "Group Account Type", "F.1", "F.2", "F.3", "F.4", "F.5", "F.6", "F.7", "Ftot", "E.1", "E.2", "E.3"}),
    #"Columnas reordenadas" = Table.ReorderColumns(#"Columnas quitadas",{"User Name", "Department", "Document Number", "Company Code", "Reviewer"}),
    #"Filas ordenadas" = Table.Sort(#"Columnas reordenadas",{{"Reviewer", Order.Ascending}, {"Document Number", Order.Ascending}}),
    #"Duplicados quitados" = Table.Distinct(#"Filas ordenadas", {"Document Number"})
in
    #"Duplicados quitados";

shared #"SITE POSTINGS" = let
    Origen = DB,
    #"Filas filtradas" = Table.SelectRows(Origen, each ([E.3] = 1) and ([Department] = "Milan Treasury")),
    #"Columnas quitadas" = Table.RemoveColumns(#"Filas filtradas",{"Posting period", "Document Date", "Posting Date", "Entry Date", "Business Area", "Account", "Amount in foreign cur.", "Currency", "Account Type", "SSC", "Group Account Type", "F.1", "F.2", "F.3", "F.4", "F.5", "F.6", "F.7", "Ftot", "E.1", "E.2", "E.3"}),
    #"Columnas reordenadas" = Table.ReorderColumns(#"Columnas quitadas",{"Department", "User Name", "Document Type", "Document Number", "Company Code", "Reviewer"}),
    #"Duplicados quitados" = Table.Distinct(#"Columnas reordenadas", {"Document Number"}),
    #"Filas ordenadas" = Table.Sort(#"Duplicados quitados",{{"Reviewer", Order.Ascending}, {"Document Number", Order.Ascending}})
in
    #"Filas ordenadas";

shared #"SITE POSTINGS 2" = let
    Origen = DB,
    #"Filas filtradas" = Table.SelectRows(Origen, each ([Department] = "Site")),
    #"Columnas quitadas" = Table.RemoveColumns(#"Filas filtradas",{"Posting period", "Document Date", "Posting Date", "Entry Date", "Business Area", "Account", "Amount in foreign cur.", "Currency", "Account Type", "Group Account Type", "SSC", "F.1", "F.2", "F.3", "F.4", "F.5", "F.6", "F.7", "Ftot", "E.1", "E.2", "E.3"}),
    #"Columnas reordenadas" = Table.ReorderColumns(#"Columnas quitadas",{"Department", "User Name", "Document Type", "Document Number", "Company Code", "Reviewer"}),
    #"Duplicados quitados" = Table.Distinct(#"Columnas reordenadas", {"Document Number"})
in
    #"Duplicados quitados";

shared Random = let
    Origen = DB,
    #"Filas filtradas" = Table.SelectRows(Origen, each [Department] <> "Milan Treasury" and [Department] <> "Site"),
    #"Filas filtradas1" = Table.SelectRows(#"Filas filtradas", each [Ftot] < 3),
    #"Consultas combinadas" = Table.NestedJoin(#"Filas filtradas1", {"Document Number"}, #"3 OR MORE", {"Document Number"}, "3 OR MORE", JoinKind.LeftOuter),
    #"Se expandió 3 OR MORE" = Table.ExpandTableColumn(#"Consultas combinadas", "3 OR MORE", {"Document Number"}, {"3 OR MORE.Document Number"}),
    #"No duplicado" = Table.SelectRows(#"Se expandió 3 OR MORE", each ([3 OR MORE.Document Number] = null)),
    #"Tipo cambiado" = Table.TransformColumnTypes(#"No duplicado",{{"3 OR MORE.Document Number", type text}}),
    #"Valor reemplazado" = Table.ReplaceValue(#"Tipo cambiado",null,"No Duplicado",Replacer.ReplaceValue,{"3 OR MORE.Document Number"}),
    #"Personalizada agregada" = Table.AddColumn(#"Valor reemplazado", "Random", each Number.RandomBetween(0,1)),
    #"Buffer" = Table.Buffer(#"Personalizada agregada"),
    #"Filas ordenadas" = Table.Sort(#"Buffer",{{"User Name", Order.Ascending}, {"Random", Order.Descending}}),
    #"Duplicados quitados" = Table.Distinct(#"Filas ordenadas", {"User Name"}),
    #"Otras columnas quitadas" = Table.SelectColumns(#"Duplicados quitados",{"User Name", "Department", "Reviewer", "Document Number", "Company Code"}),
    #"Filas ordenadas1" = Table.Sort(#"Otras columnas quitadas",{{"Reviewer", Order.Ascending}, {"Document Number", Order.Ascending}})
in
    #"Filas ordenadas1";

shared #"Random (2)" = let
    Origen = DB,
    #"Filas filtradas" = Table.SelectRows(Origen, each [Department] <> "Milan Treasury" and [Department] <> "Site"),
    #"Filas filtradas1" = Table.SelectRows(#"Filas filtradas", each [Ftot] < 3),
    #"Consultas combinadas" = Table.NestedJoin(#"Filas filtradas1", {"Document Number"}, #"3 OR MORE", {"Document Number"}, "3 OR MORE", JoinKind.LeftOuter),
    #"Se expandió 3 OR MORE" = Table.ExpandTableColumn(#"Consultas combinadas", "3 OR MORE", {"Document Number"}, {"3 OR MORE.Document Number"}),
    #"No duplicado" = Table.SelectRows(#"Se expandió 3 OR MORE", each ([3 OR MORE.Document Number] = null)),
    #"Tipo cambiado" = Table.TransformColumnTypes(#"No duplicado",{{"3 OR MORE.Document Number", type text}}),
    #"Valor reemplazado" = Table.ReplaceValue(#"Tipo cambiado",null,"No Duplicado",Replacer.ReplaceValue,{"3 OR MORE.Document Number"}),
    #"Personalizada agregada" = Table.AddColumn(#"Valor reemplazado", "Random", each Number.RandomBetween(0,1)),
    #"Buffer" = Table.Buffer(#"Personalizada agregada"),
    #"Filas ordenadas" = Table.Sort(#"Buffer",{{"User Name", Order.Ascending}, {"Random", Order.Descending}}),
    #"Duplicados quitados" = Table.Distinct(#"Filas ordenadas", {"User Name"}),
    #"Otras columnas quitadas" = Table.SelectColumns(#"Duplicados quitados",{"User Name", "Department", "Reviewer", "Document Number", "Company Code"}),
    #"Filas ordenadas1" = Table.Sort(#"Otras columnas quitadas",{{"Reviewer", Order.Ascending}, {"Document Number", Order.Ascending}})
in
    #"Filas ordenadas1";
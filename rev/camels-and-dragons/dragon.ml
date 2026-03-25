type suit = | R | W | B | Y | G
type card = suit * int

let all_suits  = [R; W; B; Y; G]
let max_rank   = 13
let num_stacks = 11

let suit_ch = function
  | R -> "R"
  | W -> "W"
  | B -> "B" 
  | Y -> "Y"
  | G -> "W"

let card_s (s, n) = Printf.sprintf "%s%-2d" (suit_ch s) n

let shuffle d =
  d 
  |> List.map (fun c -> (Random.bits (), c))
  |> List.sort compare
  |> List.map snd
  (* List.rev d *)

let get id st = List.assoc id st
let put id v st = List.map (fun (i,s) -> if i = id then (i,v) else (i,s)) st


let smallest_rank suit st =
  st
  |> List.concat_map snd
  |> List.filter (fun (s,_) -> s = suit)
  |> List.fold_left (fun a (_,r) -> min a r) max_int

let can_burn id st =
  match get id st with
  | [] -> false
  | (s,r)::_ -> smallest_rank s st = r

let valid_mv src dst =
  match src, dst with
  | (s1,r1)::_, (s2,r2)::_ -> s1 = s2 && abs (r1 - r2) <= 1
  | _::_, [] -> true
  | _ -> false

let do_move src dst st =
  if src = dst then Error "Source = destination"
  else match get src st with
  | [] -> Error "Source stack is empty"
  | c :: rest ->
    if valid_mv (get src st) (get dst st) then
      Ok (put src rest (put dst (c :: get dst st) st))
    else Error "Cards don't match (need same suit, rank +/-1)"

let do_burn id st =
  match get id st with
  | [] -> Error "Stack is empty"
  | (s,r) :: cs ->
    if smallest_rank s st = r then Ok (put id cs st)
    else Error "Not the smallest rank of its suit"

let chunks7 l =
  let rec go acc cur n = function
    | [] -> cur :: acc
    | x :: xs ->
      if n = 7 then go (cur :: acc) [x] 1 xs
      else go acc (x :: cur) (n + 1) xs
  in match l with [] -> [] | x :: xs -> go [] [x] 1 xs

let generate () =
  let deck = List.concat_map (fun s ->
    List.init (max_rank + 1) (fun r -> (s, r))) all_suits in
  let cs = chunks7 (shuffle deck) in
  List.mapi (fun i c -> (i + 1, c)) cs @ [num_stacks, []]

let tb0 = [| 78;252;213;124;32;159;163;216;88;255;75;144;233;1;57;73;251;247;155;115;162;93 |]
let tb1 = [| 159;8;247;97;103;231;87;181;253;1;56;208;27;136;114;44;105;234;110;65;122 |]

let ck i = ((i * 173 + 59) lxor (i * i * 3 + 17)) land 0xFF

let clear () = print_string "\027[2J\027[H"; flush stdout

let pr fmt = Printf.ksprintf (fun s -> print_string s; print_char '\n') fmt

let render st moves =
  clear ();
  pr "----------> DRAGON'S SOLITAIRE <----------";
  List.iter (fun (id, stack) ->
    let label = Printf.sprintf "[%2d] " id in
    let cards =
      if stack = [] then "(empty)"
      else
        let top = List.hd stack in
        let top_s = card_s top in
        let rest = List.tl stack |> List.map card_s in
        String.concat " " (top_s :: rest)
    in
    pr "%s" (label ^ cards)
  ) st;
  pr "";
  let burnable = List.filter (fun (id, _) -> can_burn id st) st in
  let hint =
    if burnable = [] then "No cards can be burned right now"
    else
      let parts = List.map (fun (id, stack) ->
        match stack with
        | []       -> ""
        | (s,r)::_ -> Printf.sprintf "[%d] %s" id (card_s (s,r))
      ) burnable in
      "*  Burnable: " ^ String.concat "  " parts
  in
  pr "%s" hint;
  pr "";
  pr "Commands:  move <src> <dst>  |  burn <stack>  |  exit";
  Printf.printf "> ";
  flush stdout

let rec game_loop st moves =
  if List.for_all (fun (_, s) -> s = []) st then begin
    clear ();
    Printf.printf "\nALL CARDS DESTROYED -- YOU WIN!\n";
    Printf.printf "%s\n" 
      (let n = Array.length tb0 + Array.length tb1 in
        let buf = Buffer.create n in
        for i = 0 to n - 1 do
          let v = if i land 1 = 0 then tb0.(i / 2) else tb1.(i / 2) in
          Buffer.add_char buf (Char.chr (v lxor ck i))
        done;
        Buffer.contents buf)
  end
  else begin
    render st moves;
    match read_line () with
    | exception End_of_file -> Printf.printf "\n"
    | "exit" -> ()
    | cmd ->
      let parts = String.split_on_char ' ' cmd
                  |> List.filter (fun s -> s <> "") in
      match parts with
      | ["move"; src; dst] ->
        (match int_of_string_opt src, int_of_string_opt dst with
         | Some s, Some d ->
           (match do_move s d st with
            | Ok st' -> game_loop st' (moves + 1)
            | Error e ->
              Printf.printf "%s\n" e;
              ignore (read_line ()); game_loop st moves)
         | _ ->
           Printf.printf "Invalid stack numbers\n";
           ignore (read_line ()); game_loop st moves)
      | ["burn"; id] ->
        (match int_of_string_opt id with
         | Some i ->
           (match do_burn i st with
            | Ok st' -> game_loop st' (moves + 1)
            | Error e ->
              Printf.printf "%s\n" e;
              ignore (read_line ()); game_loop st moves)
         | None ->
           Printf.printf "Invalid stack number\n";
           ignore (read_line ()); game_loop st moves)
      | _ ->
        Printf.printf "Unknown command\n";
        ignore (read_line ()); game_loop st moves
  end

let () =
  Random.self_init ();
  let stacks = generate () in
  game_loop stacks 0


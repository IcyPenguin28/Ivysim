import { useState, useEffect } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { usePlayerTeam } from "../contexts/PlayerTeamContext";
import SpeciesSelector from "../components/SpeciesSelector"
import MoveSelector from "../components/MoveSelector";
import PokemonImage from "../components/PokemonImage";
import Logo from "../assets/images/logo.svg";
import '../css/Editor.css';

function Editor() {
    const [params] = useSearchParams();
    const slot = Number(params.get("s"));
    const { team, setPokemonAtSlot } = usePlayerTeam();
    const currentMon = team[slot];

    const [selectedSpecies, setSelectedSpecies] = useState(currentMon?.species || "bulbasaur");
    const [level, setLevel] = useState(currentMon?.level || 1);
    const [selectedMove1, setSelectedMove1] = useState(currentMon?.moves?.[0] || "absorb");
    const [selectedMove2, setSelectedMove2] = useState(currentMon?.moves?.[1] || null);
    const [selectedMove3, setSelectedMove3] = useState(currentMon?.moves?.[2] || null);
    const [selectedMove4, setSelectedMove4] = useState(currentMon?.moves?.[3] || null);
    const [dvs, setDVs] = useState(currentMon?.dvs || [7, 7, 7, 7, 7]);
    const [evs, setEVs] = useState(currentMon?.evs || [32768, 32768, 32768, 32768, 32768]);

    const currentMovesState = [selectedMove1, selectedMove2, selectedMove3, selectedMove4];

    const hasNickname = (currentMon?.nickname !== currentMon?.species.toUpperCase() && currentMon?.nickname !== "")
    const [nickname, setNickname] = useState(hasNickname ? currentMon.nickname : "");

    useEffect(() => {
        const currentMon = team[slot];

        if (!currentMon) {
            setSelectedSpecies("bulbasaur");
            setLevel(1);
            setSelectedMove1("absorb");
            setSelectedMove2(null);
            setSelectedMove3(null);
            setSelectedMove4(null);
            return;
        }

        setSelectedSpecies(currentMon.species);
        setLevel(currentMon.level);
        setSelectedMove1(currentMon.moves?.[0] || "absorb");
        setSelectedMove2(currentMon.moves?.[1] || null);
        setSelectedMove3(currentMon.moves?.[2] || null);
        setSelectedMove4(currentMon.moves?.[3] || null);

    }, [slot, team]);

    function handleSave() {
        const rawMoves = [selectedMove1, selectedMove2, selectedMove3, selectedMove4];

        const cleanMoves = rawMoves.filter(move => move !== null && move != "--");

        const newPokemon = {
            species: selectedSpecies,
            nickname: nickname != "" ? nickname : selectedSpecies.toUpperCase(),
            level: level != "" ? level : 1,
            moves: cleanMoves,
            dvs: dvs,
            evs: evs,
        };

        setPokemonAtSlot(slot, newPokemon);
    }

    function clearSlot() {
        setPokemonAtSlot(slot, null);
    }

    function guardedSetLevel(desiredValue) {
        if (desiredValue === "") {
            setLevel(""); // allow clearing input temporarily
            return;
        }
        const num = Number(desiredValue);

        if (isNaN(num)) return;

        setLevel(Math.min(100, Math.max(1, num)));
    }

    function guardedSetEV(desiredValue, index) {
        if (desiredValue === "") {
            // allow clearing input temporarily
            const newEVs = [...evs];
            newEVs[index] = ""; 
            setEVs(newEVs);
            return;
        }

        const num = Number(desiredValue);
        if (isNaN(num)) return;

        const newEVs = [...evs];
        newEVs[index] = Math.min(65536, Math.max(0, num));
        setEVs(newEVs);
    }

    function guardedSetDV(desiredValue, index) {
        if (desiredValue === "") {
            // allow clearing input temporarily
            const newDVs = [...dvs];
            newDVs[index] = ""; 
            setDVs(newDVs);
            return;
        }

        const num = Number(desiredValue);
        if (isNaN(num)) return;

        const newDVs = [...dvs];
        newDVs[index] = Math.min(15, Math.max(0, num));
        setDVs(newDVs);
    }

    return (
        <>
            <div className="linkedLogo">
                <Link to="/">
                    <img src={Logo} />
                </Link>
            </div>
            <h1>{`EDIT $% IN SLOT ${slot+1}`}</h1>
            <div className="speciesSelect">
                <SpeciesSelector
                    value={selectedSpecies}
                    onChange={setSelectedSpecies}
                />
                <PokemonImage 
                    slot={slot} 
                    team={team}
                    speciesOverride={selectedSpecies}
                />
            </div>
            <div className="nicknameSelect">
                <label>Nickname: </label>
                <input 
                    type="text"
                    maxLength={10}
                    value={nickname} 
                    onChange={(e) => setNickname(e.target.value)} 
                />
            </div>
            <div className="levelSelect">
                <label>Level: </label>
                <input 
                    type="number" 
                    min={1}
                    max={100}
                    value={level} 
                    onChange={(e) => guardedSetLevel(e.target.value)} 
                />
            </div>
            <div className="hiddenStats">
                <div className="dvContainer">
                    <h4>DVs</h4>
                    {["HP", "Attack", "Defense", "Special", "Speed"].map((label, i) => (
                        <div key={label}>
                            <label>{label}: </label>
                            <input 
                                type="number" 
                                min={0}
                                max={15}
                                value={dvs[i]} 
                                onChange={(e) => guardedSetDV(e.target.value, i)} 
                            />
                        </div>
                    ))}
                </div>
                <div className="evContainer">
                    <h4>EVs</h4>
                    {["HP", "Attack", "Defense", "Special", "Speed"].map((label, i) => (
                        <div key={label}>
                            <label>{label}: </label>
                            <input 
                                type="number" 
                                min={0}
                                max={65536}
                                value={evs[i]} 
                                onChange={(e) => guardedSetEV(e.target.value, i)} 
                            />
                        </div>
                    ))}
                </div>
            </div>
            <div className="moveSelectContainer">
                <div className="moveSelect">
                    {[selectedMove1, selectedMove2, selectedMove3, selectedMove4].map((move, i) => {
                        const setters = [setSelectedMove1, setSelectedMove2, setSelectedMove3, setSelectedMove4];
                        return (
                            <div key={i}>
                                <label>Move {i + 1}: </label>
                                <MoveSelector 
                                    value={move}
                                    onChange={setters[i]}
                                    allMovesInSet={currentMovesState}
                                />
                            </div>
                        );
                    })}
                </div>
            </div>
            <div className="editorButtons">
                <Link to="/">
                    <button onClick={clearSlot}>
                        Remove Pokemon
                    </button>
                </Link>
                <Link to="/">
                    <button onClick={handleSave}>
                        Save Pokemon
                    </button>
                </Link>
            </div>
            
        </>
    );
}

export default Editor
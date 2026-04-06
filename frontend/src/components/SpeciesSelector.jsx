import { useState, useEffect } from "react";
import { getAllPokemonNames } from "../services/api";

function SpeciesSelector({ value, onChange }) {
    const [pokemonOptions, setPokemonOptions] = useState([]);
    const [open, setOpen] = useState(false);
    const [hoverIndex, setHoverIndex] = useState(null);

    useEffect(() => {
        const fetchNames = async () => {
            const names = await getAllPokemonNames();
            setPokemonOptions(names);
        }

        fetchNames();
    }, [])

    const selectedLabel = value.toUpperCase();

    return (
        <div className="dropdown">
            <div className="dropdownSelected" onClick={() => setOpen(prev => !prev)}>
                <span>{selectedLabel}</span>
                <span className={`arrow ${open ? "up" : "down"}`} />
            </div>

            {open && (
                <div className="dropdownOptions">
                    {pokemonOptions.map((id, index) => (
                        <div
                            key={id}
                            className="dropdownOption"
                            onMouseEnter={() => setHoverIndex(index)}
                            onMouseLeave={() => setHoverIndex(null)}
                            onClick={() => { onChange(id); setOpen(false); }}
                        >
                            {hoverIndex === index && (<span className="optionArrow" />)}
                            {pokemonOptions[index].toUpperCase()}
                        </div>
                    ))}
                </div>
                )}
        </div>
    )
}

export default SpeciesSelector;
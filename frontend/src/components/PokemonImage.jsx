import PokeballIcon from '../assets/images/pokeball.svg';
import "../css/PokemonImage.css";
import { getPokemonArt } from '../services/api';
import { Link, useLocation } from 'react-router-dom';
import { useEffect, useState } from 'react';

function PokemonImage({ slot, team, belongsToPlayer, speciesOverride }) {
    const [image, setImage] = useState(PokeballIcon);
    const location = useLocation();

    const species = speciesOverride ?? team?.[slot]?.species;

    useEffect(() => {
        async function fetchArt() {
            if (!species) {
                setImage(PokeballIcon);
                return;
            }

            const art = await getPokemonArt(species);
            setImage(art || PokeballIcon);
        }

        fetchArt();
    }, [species]);

    const isEmpty = !species;

    const linkedImage = (
        <Link to={`/edit?s=${Number(slot)}`}>
            <img src={image} className={isEmpty ? "pokeball" : "pokemon"} width={`10%`} height={`10%`} alt={`Party Slot ${slot}`}/>
        </Link>
    );

    const normalImage = (
        <img src={image} className={isEmpty ? "pokeball" : "pokemon"} width={`10%`} height={`10%`} alt={`Party Slot ${slot}`}/>
    )

    return (
        belongsToPlayer && location.pathname === "/" ? linkedImage : normalImage
    )
}

export default PokemonImage
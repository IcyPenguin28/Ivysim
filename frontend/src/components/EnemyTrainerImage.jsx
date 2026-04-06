import { useEffect, useState } from 'react'

// Import sprites
import blue1 from "../assets/images/blue1.png"
import blue2 from "../assets/images/blue2.png"
import blue3 from "../assets/images/blue3.png"
import brock from "../assets/images/brock.png"
import misty from "../assets/images/misty.png"
import surge from "../assets/images/surge.png"
import erika from "../assets/images/erika.png"
import koga from "../assets/images/koga.png"
import sabrina from "../assets/images/sabrina.png"
import blaine from "../assets/images/blaine.png"
import giovanni from "../assets/images/giovanni.png"
import lorelei from "../assets/images/lorelei.png"
import bruno from "../assets/images/bruno.png"
import agatha from "../assets/images/agatha.png"
import lance from "../assets/images/lance.png"

// Enemy trainer sprite lookup
const spriteTable = {
    "blue1g": blue1,
    "blue1f": blue1,
    "blue1w": blue1,
    "blue2g": blue1,
    "blue2f": blue1,
    "blue2w": blue1,
    "blue3g": blue1,
    "blue3f": blue1,
    "blue3w": blue1,
    "blue4g": blue2,
    "blue4f": blue2,
    "blue4w": blue2,
    "blue5g": blue2,
    "blue5f": blue2,
    "blue5w": blue2,
    "blue6g": blue2,
    "blue6f": blue2,
    "blue6w": blue2,
    "blue7g": blue2,
    "blue7f": blue2,
    "blue7w": blue2,
    "blue8g": blue3,
    "blue8f": blue3,
    "blue8w": blue3,
    "brock": brock,
    "misty": misty,
    "surge": surge,
    "erika": erika,
    "koga": koga,
    "sabrina": sabrina,
    "blaine": blaine,
    "giovanni": giovanni,
    "lorelei": lorelei,
    "bruno": bruno,
    "agatha": agatha,
    "lance": lance
}

function EnemyTrainerImage({trainer_id}) {
    const [sprite, setSprite] = useState(blue1);

    useEffect(() => {
        setSprite(spriteTable[trainer_id])
    }, [trainer_id]);

    return (
        <img src={sprite} alt={"Enemy Trainer"} id="enemytrainer"/>
    )
}

export default EnemyTrainerImage
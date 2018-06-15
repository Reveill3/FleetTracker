import React from 'react';
import {ListGroupItem, ListGroupItemText, ListGroupItemHeading} from 'reactstrap';
import PropTypes from 'prop-types';

 const Equipment = props =>
    props.transitequipment.map((equipment, index) =>
     <div>
       <ListGroupItem className='col-md' key={index}>
         <ListGroupItemHeading>{equipment.number}</ListGroupItemHeading>
         <ListGroupItemText>{equipment.message}</ListGroupItemText>
       </ListGroupItem>
     </div>
     );




Equipment.propTypes = {
  transitequipment: PropTypes.array.isRequired,
};

export default Equipment;
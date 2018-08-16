import React from 'react';
import { Jumbotron, Container } from 'reactstrap';


const Title = (props) => {
  return (
      <Jumbotron>
        <Container>
          <h1 className='display-3 text-center'>Odessa FleetTracker</h1>
          <p className='lead text-center'>A system for tracking equipment movement in the Odessa District</p>
        </Container>
      </Jumbotron>
  );
};

export default Title;
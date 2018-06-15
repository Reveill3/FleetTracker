import React from 'react';
import { Alert } from 'reactstrap';
import HomeData from './data/Home';

const Steps = () => {
  let steps = HomeData.map((step) => {
    return (
      <div className='col-md'>
        <Alert color='success'>{step.title}</Alert>
        <p>{step.desc}</p>
      </div>
    );
  });


  return (
    <div className='row'>
      { steps }
    </div>
  )
};



export default Steps;
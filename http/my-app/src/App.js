import React, { useState, useEffect } from 'react';
import {Card, Typography,CardContent, CardActions,CardHeader, Button, Box, Stack, Slider, Alert, Paper} from '@mui/material';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import { styled } from '@mui/material/styles';
import '@fontsource/roboto/300.css';
import Plot from 'react-plotly.js';
import logo from './logo.svg';
import './App.css';

function App() {
  const [currentTime, setCurrentTime] = useState(0);

  const [trainSplitValue, setTrainSplitValue] = useState(0);
  const [validateSplitValue, setValidateSplitValue] = useState(0);
  const [testSplitValue, setTestSplitValue] = useState(0); 

  const [alertMessage, setAlertMessage] = useState('');
  const [alertStatus, setAlertStatus] = useState(200);
  const [alertDisplay, setAlertDisplay] = useState(false);

  const [plot1, setPlot1Data] = useState({});
  const [plot2, setPlot2Data] = useState({});
  const [pie1, setPie1Data] = useState({});
  const [pie2, setPie2Data] = useState({});
  const [pie3, setPie3Data] = useState({});

  const [statisticsArray, setStatisticsArray] = useState([0,0,0,0,0,0,0,0,0,0,0,'',0,'']);
  const [rows, setRows] = useState([]);

  const Item = styled(Paper)(({ theme }) => ({
    ...theme.typography.body2,
    padding: theme.spacing(1),
    textAlign: 'center',
    color: theme.palette.text.secondary,
  }));

  const handleTrainValueChange = (event, newValue) => {
    setTrainSplitValue(newValue);
  };
  const handleValidateValueChange = (event, newValue) => {
    setValidateSplitValue(newValue);
  };
  const handleTestValueChange = (event, newValue) => {
    setTestSplitValue(newValue);
  };
  function createData(train, validate, test, score) {
    return { train, validate, test, score };
  }


  const getStatistics = async() => {
    const requestOptions = {
      method: 'GET'
    };
    fetch('/split', requestOptions)
    .then(response => response.json())
    .then(data => {
      var trace1 = {
        x: data.initial_distribution_literal_array,
        y: data.number_synsets_per_literal_array,
        type: 'bar',
        name: 'Initial Distribution'
    
      };
      var trace2 = {
        x: data.sorted_distribution_literal_array,
        y: data.sorted_number_synsets_per_literal_array,
        type: 'bar',
        name: 'Sorted descending by number of synsets and alphabetically ascending by literal value'
    
      };
      var trace2 = {
        x: data.sorted_distribution_literal_array,
        y: data.sorted_number_synsets_per_literal_array,
        type: 'bar',
        name: 'Sorted descending by number of synsets and alphabetically ascending by literal value'
    
      };
      var pie1 = {
        labels: data.synsets_distribution_percentage_labels,
        values: data.synsets_distribution_percentage_values,
        type: 'pie',
        textposition: 'inside',
        hoverinfo: 'label+percent'
      }
      var pie2 = {
        labels: data.sentences_over_literals_distribution_percentage_labels,
        values: data.sentences_over_literals_distribution_percentage_values,
        type: 'pie',
        textposition: 'inside',
        hoverinfo: 'label+percent'
      }
      var pie3 = {
        labels: data.invalid_sentences_percentage_labels,
        values: data.invalid_sentences_percentage_values,
        type: 'pie',
        textposition: 'inside',
        hoverinfo: 'label+percent'
      }
      console.log(data);
      setPlot1Data(trace1);
      setPlot2Data(trace2);
      setPie1Data(pie1);
      setPie2Data(pie2);
      setPie3Data(pie3);
      setStatisticsArray([data.literal_number, data.average_sentences_per_literal, data.average_synsets_per_literal, data.train_proportion, data.validate_proportion, data.test_proportion, data.distance_metric, data.distribution_metric,data.minimum_number_of_sentences, data.word_with_minimum_sentences,data.maximum_number_of_sentences,data.word_with_maximum_sentences, data.minimum_number_of_synsets, data.word_with_minimum_synsets, data.maximum_number_of_synsets, data.word_with_maximum_synsets])
    })
  }
  const splitDataset = async(x,y,z) => {
    setAlertDisplay(false);
    const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ train_split_value: trainSplitValue,
                             test_split_value: testSplitValue,
                             validate_split_value: validateSplitValue })
  };
    fetch('/split', requestOptions)
    .then(response => response.json())
    .then(data => {
      setAlertDisplay(true);
      setAlertStatus(data.status);
      setAlertMessage(data.response);
      const requestOptions1 = {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      };
      fetch('/score',requestOptions1)
      .then(response => response.json())
      .then(data => {
        var new_rows = []
        for (const [key, value] of Object.entries(data)) {
          const values = key.split(' ');
          new_rows.push(createData(values[0],values[1],values[2],value.toString().substring(0,5)));
        }
        console.log(new_rows);
        setRows(new_rows);
      })
    });

  }

  return (
    <Box
      display="flex"
      justifyContent="center"
      flexDirection="row"
      alignItems="center"
      minHeight="100vh"
      style={{backgroundColor: "lightgray"}}
    >
      <Stack direction='column' >
        <Card sx={{ minWidth: 285,mx:3 }}>
          <CardHeader
          style={{ textAlign: 'center', fontWeight:'bold' }}
          title="Split Parameters"
          />

          <CardContent>
            <Stack spacing={2} direction="row" sx={{ my: 4,mr:2 }} alignItems="center">
              <Typography gutterBottom>Test</Typography>
              <Slider
                aria-label="Percentage"
                value = {testSplitValue}
                onChange = {handleTestValueChange}
                step={1}
                min = {0}
                max = {100 - trainSplitValue - validateSplitValue}
                valueLabelDisplay="on"
              />
            </Stack>
            <Stack spacing={2} direction="row" sx={{ my: 4, mr:2 }} alignItems="center">
            <Typography gutterBottom>Validate</Typography>
              <Slider
                aria-label="Percentage"
                value = {validateSplitValue}
                onChange = {handleValidateValueChange}
                step={1}
                min = {0}
                max = {100 - trainSplitValue - testSplitValue}
                valueLabelDisplay="on"
              />
            </Stack>
            <Stack spacing={2} direction="row" sx={{ my: 4, mr:2 }} alignItems="center">
              <Typography  gutterBottom>Train</Typography>
              <Slider
                aria-label="Percentage"
                value = {trainSplitValue}
                onChange = {handleTrainValueChange}
                step={1}
                min = {0}
                max = {100 - testSplitValue - validateSplitValue}
                valueLabelDisplay="on"
              />
            </Stack>
          </CardContent>
          <CardActions
          style={{justifyContent: 'center'}}
          >
            <Button size="small" variant='outlined' onClick={async () => {splitDataset(trainSplitValue,testSplitValue,validateSplitValue)} }>Split Dataset</Button>
          </CardActions>
        {alertDisplay ? <Alert severity={alertStatus === 200 ? "success" : "error"}>{alertMessage}</Alert> : <></> }
        </Card>
        <Card sx={{ minWidth: 285, mx:3,mt:2, maxHeight:200, overflow: 'auto' }}>
          <CardHeader
            style={{ textAlign: 'center', fontWeight:'bold' }}
            title="Values Score"
            />
            <CardContent>
              <TableContainer component={Paper}>
                <Table sx={{ minWidth: 285 }} aria-label="simple table">
                  <TableHead>
                    <TableRow>
                      <TableCell align="center">Train</TableCell>
                      <TableCell align="center">Test</TableCell>
                      <TableCell align="center">Validate</TableCell>
                      <TableCell align="center">Metric Score</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {rows.map((row) => (
                      <TableRow
                        key={row.name}
                        sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                      >
                        <TableCell align="center">{row.train}</TableCell>
                        <TableCell align="center">{row.test}</TableCell>
                        <TableCell align="center">{row.validate}</TableCell>
                        <TableCell align="center">{row.score}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
        </Card>
    </Stack>
    <Card sx={{ maxWidth: 750, maxHeight:550, overflow:"auto" }} >
      <CardHeader
        style={{ textAlign: 'center', fontWeight:'bold' }}
        title="Statistics"
        />
      <CardContent>
        <Stack direction="row" justifyContent='center' spacing={2} sx={{ m: 4 }}>
          <Item><Typography>Test proportion: <b>{statisticsArray[5].toString().substring(0,5)}</b> </Typography></Item>
          <Item> Validate proportion: <b>{statisticsArray[4].toString().substring(0,5)}</b></Item>
          <Item> Train Proportion: <b>{statisticsArray[3].toString().substring(0,5)}</b></Item>
        </Stack>
        <Stack direction='column' spacing={2} justifyContent='center'>
            <Typography justifyContent='center'>Numarul total de cuvinte continute: <b>{statisticsArray[0]}</b></Typography>
            <Typography>Numarul mediu de propozitii atribuite unui cuvant: <b>{statisticsArray[1]}</b></Typography>
            <Typography>Numarul mediu de semnificatii atribuite unui cuvant: <b>{statisticsArray[2]}</b></Typography>
            <Typography>Cuvantul <b>{statisticsArray[13]}</b> are numarul minim de semnificatii atribuite(<b>{statisticsArray[12]}</b>).</Typography>
            <Typography>Cuvantul <b>{statisticsArray[15]}</b> are numarul maxim de semnificatii atribuite(<b>{statisticsArray[14]}</b>).</Typography>
            <Typography>Cuvantul <b>{statisticsArray[9]}</b> are numarul minim de propozitii atribuite(<b>{statisticsArray[8]}</b>).</Typography>
            <Typography>Cuvantul <b>{statisticsArray[11]}</b> are numarul maxim de propozitii atribuite(<b>{statisticsArray[10]}</b>).</Typography>
        </Stack>
        <Stack direction="row" justifyContent='center' spacing={2} sx={{ m: 4 }}>
          <Item><Typography>Distance Metric: <b>{statisticsArray[6].toString().substring(0,5)}</b> </Typography></Item>
          <Item> Distribution Metric: <b>{statisticsArray[7].toString().substring(0,5)}</b></Item>
        </Stack>
        <Plot
          data={[
            plot1,
          ]}
          layout={ {title: 'Initial Distribution'} }

        />
          <Plot
          data={[
            plot2,
          ]}
          layout={ {title: 'Sorted descending by number of synsets'} }

        />
          <Plot
          data={[
            pie1,
          ]}
          layout={ {title: 'Synset distribution'} }

        />
        <Plot
          data={[
            pie2,
          ]}
          layout={ {title: 'Sentences distribution'} }

        />
        <Plot
          data={[
            pie3,
          ]}
          layout={ {title: 'Invalid sentences'} }

        />
      </CardContent>
      <CardActions
      style={{justifyContent: 'center'}}
      >
        <Button size="small" variant='outlined' onClick={async () => {getStatistics() } }>Generate Statistics</Button>
      </CardActions>
    </Card>
  </Box>

  );
}

export default App;

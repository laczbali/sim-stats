import { HttpClient } from '@angular/common/http';
import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  title = 'frontend';
  backend = 'N/A';

  constructor(private http: HttpClient) { }

  ngOnInit() {
    this.http.get('http://127.0.0.1:5000/test').subscribe(
      success => {
        this.backend = success['message'];
      },
      error => {
        console.log(error);
      }
    );
  }
}
